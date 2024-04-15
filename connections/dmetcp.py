import asyncio
import sys
import logging

from butils.utils import *
from connections.abstracttcp import AbstractTcp

from medius.serializer import TcpSerializer

class DmeTcp(AbstractTcp):
    def __init__(self, loop, ip, port, session_key, access_key, world_id):
        super().__init__(loop, ip, port)
        self._logger = logging.getLogger('thug.dmetcp')
        self._logger.setLevel(logging.DEBUG)

        self.session_key = session_key
        self.access_key = access_key
        self.world_id = world_id

        self.dmeudp_ip = None
        self.dmeudp_port = None

        self.player_id = None
        self.player_count = 0

        self.loop.run_until_complete(self.start())


    async def main(self, model):
        while model.alive:
            if self.qsize() != 0:
                packet = self.dequeue()
                try:
                    serialized = TcpSerializer[packet[0]]['serializer'].serialize(packet)
                    model.process(serialized)
                except:
                    self._logger.exception(f"Error processing DME TCP packet")
            await asyncio.sleep(0.0001)

    async def connect(self):
        await asyncio.wait_for(self.connect_to_dme_world_stage_1(), timeout=5.0)

    async def connect_to_dme_world_stage_1(self):
        # Initial connect to DME TCP
        self._logger.info("Connecting to dme world Stage [1] ...")
        pkt = hex_to_bytes('156A00010801')
        pkt += int_to_bytes_little(2, self.world_id-1)
        #pkt += int_to_bytes_little(2, 1)
        pkt += hex_to_bytes('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self.session_key
        pkt += self.access_key

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x07:
                raise Exception('Unknown response!')

            elif data[0] == 0x07:
                self._logger.info(bytes_to_hex(data))
                self.player_id = bytes_to_int_little(data[6:8])
                self.player_count = bytes_to_int_little(data[8:10])
                break


        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x18:
                raise Exception('Unknown response!')

            elif data[0] == 0x18:
                self._logger.info(bytes_to_hex(data))

            data = bytes_to_hex(data)
            data = deque([data[i:i+2] for i in range(0,len(data),2)])
            buf = ''.join([data.popleft() for _ in range(3)])
            self.dmeudp_ip = hex_to_str(''.join([data.popleft() for _ in range(16)]))
            self.dmeudp_port = hex_to_int_little(''.join([data.popleft() for _ in range(2)]))
            break

        self._logger.info(f"Connected Stage [1]! Player ID: {self.player_id} | Player count: {self.player_count}")


    async def connect_final(self):
        await asyncio.wait_for(self.connect_to_dme_world_stage_2(), timeout=5.0)

    async def connect_to_dme_world_stage_2(self):
        self._logger.info("Connecting to dme world Stage [2] ...")
        pkt = hex_to_bytes('170000')

        self.queue(pkt)
        self._logger.info("Connected Stage [2]!")


