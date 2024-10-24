import json
import logging
import os
import asyncio
from collections import deque
from datetime import datetime

# requirements packages
import websockets

import sys
sys.path.append('..')

# package imports
from medius.dme_serializer import TcpSerializer as tcp_map
from medius.dme_serializer import UdpSerializer as udp_map
from medius.dme_serializer import packets_both_tcp_and_udp

from live.world_manager import WorldManager



class LiveTrackerBackend:
    def __init__(self, server_ip='0.0.0.0', simulated:bool=False, log_level='INFO', error_retry_time=10, run_blocked=False):
        self.logger = logging.getLogger('uyalive')
        formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.getLevelName(log_level))
        sh.setLevel(logging.DEBUG)
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.getLevelName(log_level))

        self.simulated = simulated
        self.simulated_queue = deque()

        self.server_ip = server_ip
        self.error_retry_time = error_retry_time # in seconds
        self.run_blocked = run_blocked

        self._world_manager = None
        
        self.connected = False

    def start(self, loop):
        self._world_manager = WorldManager(simulated=self.simulated)

        loop.create_task(self.world_check_timeouts())

        self.loop = loop
        if self.run_blocked: # For debugging
            loop.create_task(self.read_websocket())
            while True:
                self.logger.info(self.get_world_states())
                loop.run_until_complete(self.wait())
        elif self.simulated:
            loop.create_task(self.read_simulated_data())
            loop.create_task(self.read_simulated_websocket())
        else:
            loop.create_task(self.read_websocket())

    async def wait(self):
        await asyncio.sleep(5)
    
    def get_world_states(self) -> dict:
        '''
        Return dictionary format of world game stats
        '''
        return self._world_manager.to_json()

    async def world_check_timeouts(self):
        while True:
            # Check if any worlds have not received updates
            self._world_manager.check_timeouts()
            await asyncio.sleep(10)

    async def read_simulated_websocket(self):
        self.logger.info("Simulating websocket data from file!")
        while True:
            try:
                while True:
                    data = await self.simulated_read()
                    self.logger.debug(f"{data}")
                    try:
                        for data_point in data:
                            serialized_data = self.process(data_point)
                            for serialized in serialized_data:
                                self._world_manager.update(data_point, serialized)
                    except Exception as e:
                        self.logger.warning(f"Error processing: {e}")

            except Exception as e:
                self.logger.warning(f"UYA Live error reading simulated websocket: {e}")
                self.logger.warning(f"Waiting {self.error_retry_time} seconds for next retry ...")
                await asyncio.sleep(self.error_retry_time)

    async def read_simulated_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, 'live', 'simulated_data.json') ,'r') as f:
            data = f.readlines()
        data = [eval(line.strip()) for line in data]

        data[0]['sleep'] = 0
        for i in range(1,len(data)):
            ts_before = datetime.strptime(data[i-1]['ts'], '%Y-%m-%d %H:%M:%S.%f')
            ts_current = datetime.strptime(data[i]['ts'], '%Y-%m-%d %H:%M:%S.%f')
            diff_seconds = (ts_current - ts_before).total_seconds()
            data[i]['sleep'] = diff_seconds

        while True:
            self._world_manager.reset()
            self.simulated_queue = deque()

            for datapoint in data:
                await asyncio.sleep(datapoint['sleep'])
                self.simulated_queue.append(datapoint['data'])

    async def simulated_read(self):
        while len(self.simulated_queue) == 0:
            await asyncio.sleep(0.00001)
        return self.simulated_queue.popleft()


    async def read_websocket(self):
        uri = f"ws://{self.server_ip}:8765"
        while True:
            try:
                async with websockets.connect(uri,ping_interval=None) as websocket:
                    self.logger.info("Connected to websocket!")
                    self.connected = True
                    while True:
                        data = await websocket.recv()
                        self.logger.debug(f"{data}")
                        try:
                            for data_point in json.loads(data):
                                serialized_data = self.process(data_point)
                                for serialized in serialized_data:
                                    self._world_manager.update(data_point, serialized)
                        except Exception as e:
                            self.logger.warning(f"Error processing: {e}")


            except Exception as e:
                self.logger.warning(f"UYA Live error reading websocket: {e}")
                self.logger.warning(f"Waiting {self.error_retry_time} seconds for next retry ...")
                self.connected = False
                await asyncio.sleep(self.error_retry_time)

    def process(self, packet: dict):
        '''
        Process json from Robo's websocket.
        Structure:
        {
            "type": udp/tcp
            "dme_world_id": int
            "src": the source player dme id
            "dst": the destination player dme id, -1 for sending to all
            "data": a hex string of the raw data
        }
        '''
        # Convert to list. E.g. '000102030405' -> ['00', '01', '02', '03', '04', '05']
        data = deque([packet['data'][i:i+2] for i in range(0,len(packet['data']),2)])

        '''
        There may be multiple messages in each message.
        So we have to read the current message, and see if there's any leftover
        data which would be another message
        '''
        all_serialized = []
        # Keep reading until data is empty
        while len(data) != 0:
            packet_id = data.popleft() + data.popleft() # E.g. '0201'

            # Check if the packet_id exists. If it does, serialize it
            if packet['type'] == 'tcp':
                if packet_id not in tcp_map.keys():
                    break
                else:
                    if packet_id in packets_both_tcp_and_udp:
                        serialized = tcp_map[packet_id].serialize('tcp', data)
                    else:
                        serialized = tcp_map[packet_id].serialize(data)

            elif packet['type'] == 'udp':
                if packet_id not in udp_map.keys():
                    break
                else:
                    if packet_id in packets_both_tcp_and_udp:
                        serialized = udp_map[packet_id].serialize('udp', data)
                    else:
                        serialized = udp_map[packet_id].serialize(data)


            all_serialized.append(serialized)

        self.logger.debug(f"{packet} -> {[str(s) for s in all_serialized]}")
        return all_serialized




if __name__ == '__main__':
    # pip install git+https://github.com/Horizon-Private-Server/horizon-uya-bot.git
    # from livetrackerbackend import LiveTrackerBackend
    import os
    import asyncio
    import json
    loop = asyncio.new_event_loop()
    tracker = LiveTrackerBackend(server_ip=os.getenv('SOCKET_IP'), log_level='INFO')

    tracker.start(loop)

    while True:
        world_information = tracker.get_world_states()
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print("===========================================================================")
        print(json.dumps(world_information, indent=4))
        loop.run_until_complete(asyncio.sleep(1))

