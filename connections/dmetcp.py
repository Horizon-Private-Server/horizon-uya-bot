import asyncio
import sys
import logging

from utils.utils import *
from connections.abstracttcp import AbstractTcp

from medius.serializer import TcpSerializer

class DmeTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.dmetcp')
        self._logger.setLevel(logging.WARNING)


        self._player_id = None
        self._player_count = 0

        self.loop.run_until_complete(self.start())
        self.loop.create_task(self.read())
        self.loop.create_task(self.write())
        self.loop.create_task(self.echo())


    async def main(self, model):
        while True:
            if self.qsize() != 0:
                packet = self.dequeue()
                serialized = TcpSerializer[packet[0]]['serializer'].serialize(packet)
                try:
                    model.process(serialized)
                except:
                    logger.exception()
            await asyncio.sleep(0.0001)

    async def connect_to_dme_world_stage_1(self, access_key):
        # Initial connect to DME TCP
        self._logger.info("Connecting to dme world Stage [1] ...")
        pkt = hex_to_bytes('156B00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += hex_to_bytes('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += access_key

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
                self._player_id = bytes_to_int_little(data[6:8])
                self._player_count = bytes_to_int_little(data[8:10])
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
                break

        self._logger.info(f"Connected Stage [1]! Player ID: {self._player_id} | Player count: {self._player_count}")

    async def connect_to_dme_world_stage_2(self):
        self._logger.info("Connecting to dme world Stage [2] ...")
        pkt = hex_to_bytes('170000')

        self.queue(pkt)
        self._logger.info("Connected Stage [2]!")


    def get_player_id(self):
        return self._player_id

    def get_player_count(self):
        return self._player_count
