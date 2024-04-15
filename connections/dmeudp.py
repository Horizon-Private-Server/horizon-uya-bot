import asyncio
import logging

from butils.utils import *
from connections.abstractudp import AbstractUdp

from medius.serializer import UdpSerializer

from datetime import datetime

class DmeUdp(AbstractUdp):
    def __init__(self, loop, ip: str, port: int, world_id: int, player_id: int):
        super().__init__(loop, ip, port)
        self._logger = logging.getLogger('thug.dmeudp')
        self._logger.setLevel(logging.DEBUG)

        self.loop.create_task(self.start())
        self.loop.run_until_complete(asyncio.sleep(.25))
        self.loop.create_task(self.write())

        self.world_id = world_id
        self.player_id = player_id

    async def connect(self):
        await asyncio.wait_for(self.connect_to_dme_world(), timeout=5.0)

    async def connect_to_dme_world(self):
        self._logger.info("Connecting to UDP dme world ...")
        pkt = hex_to_bytes('161D00010801')
        pkt += int_to_bytes_little(2, self.world_id)
        pkt += hex_to_bytes('BC290000')
        pkt += str_to_bytes(self._ip, 16)
        pkt += int_to_bytes_little(2, self._port)
        pkt += int_to_bytes_little(2, self.player_id)

        self.queue(pkt)

        started = datetime.now().timestamp()
        while True:
            # Check the result
            data = self.dequeue()

            if datetime.now().timestamp() - started > 4: # 4 second timeout
                raise Exception('UDP Timeout!')

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x19:
                raise Exception('Unknown response!')

            elif data[0] == 0x19:
                self._player_id = bytes_to_int_little(data[6:8])
                self._player_count = bytes_to_int_little(data[8:10])
                break

        self._logger.info("Connected!")

    async def main(self, model):
        while model.alive:
            if self.qsize() != 0:
                packet = self.dequeue()
                try:
                    serialized = UdpSerializer[packet[0]]['serializer'].serialize(packet)
                    model.process(serialized)
                except:
                    self._logger.exception(f"Error processing DME UDP packet")
            await asyncio.sleep(0.0001)
