import asyncio
import logging

from utils.utils import *
from connections.abstractudp import AbstractUdp

from medius.serializer import RtSerializer

class DmeUdp(AbstractUdp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.dmeudp')
        self._logger.setLevel(logging.INFO)

        self.loop.create_task(self.start())
        self.loop.run_until_complete(asyncio.sleep(1))
        self.loop.create_task(self.write())
        self.loop.create_task(self.echo())

    async def connect_to_dme_world(self, player_id):
        self._logger.info("Connecting to dme world ...")
        pkt = hex_to_bytes('161D00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += hex_to_bytes('BC290000')
        pkt += str_to_bytes(self._ip, 16)
        pkt += int_to_bytes_little(2, self._port)
        pkt += int_to_bytes_little(2, player_id)

        self.queue(pkt)

        await asyncio.sleep(2)

        data = self.dequeue()
        if data[0] != 0x19:
            raise Exception('Unknown response!')

        self._logger.info("Connected!")

    async def main(self, model):
        while True:
            if self.qsize() != 0:
                packet = self.dequeue()
                serialized = RtSerializer[packet[0]]['serializer'].serialize(packet)
                serialized['protocol'] = 'UDP'
                model.process(serialized)
            await asyncio.sleep(self._wait_time_for_packets)
