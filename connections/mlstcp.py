import asyncio
import sys
import logging

from utils.utils import *
from connections.abstracttcp import AbstractTcp


class MlsTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.mlstcp')
        self._logger.setLevel(logging.WARNING)

        self._access_key = None

        self.loop.run_until_complete(self.start())
        self.loop.create_task(self.read())
        self.loop.create_task(self.write())
        self.loop.run_until_complete(self.generate_access_key())
        self.loop.create_task(self.echo())
        self.loop.run_until_complete(self.connect_to_mls())

    async def generate_access_key(self):
        self._logger.info("Generating access key ...")

        # Join game packet
        join_game_p1 = '0BC60001F331000000000000000000000000000000000000000000000000000000000000000000000000000000'
        join_game_p2 = '0000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        message = hex_to_bytes(join_game_p1 + bytes_to_hex(int_to_bytes_little(4, self._config['world_id'])) + join_game_p2)

        self.queue(message)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x0A or data[1] != 0xBC:
                raise Exception('Unknown response!')

            elif data[0] == 0x0A and data[1] == 0xBC:
                self._access_key = data[174:]
                self._logger.info("Access key generated!")
                break

    async def connect_to_mls(self):
        self._logger.info("Connecting to MLS ...")
        pkt = hex_to_bytes('006B000108010000BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

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
                break

        while True:
            # Check the result
            data = self.dequeue()

            if data[0] != 0x1A:
                raise Exception('Unknown response!')

            elif data[0] == 0x1A:
                break
        self._logger.info("Connected!")

    def get_access_key(self):
        self.loop.run_until_complete(self.generate_access_key())
        return self._access_key
