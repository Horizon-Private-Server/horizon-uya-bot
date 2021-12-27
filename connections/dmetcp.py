import asyncio
import sys
import logging

from utils import *
from connections.abstracttcp import AbstractTcp


class DmeTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.dmetcp')
        self._logger.setLevel(logging.DEBUG)


        self._player_id = None
        self._player_count = 0

        self.loop.run_until_complete(self.start())
        self.loop.create_task(self.read())
        self.loop.create_task(self.write())
        self.loop.create_task(self.echo())


    async def connect_to_dme_world_stage_1(self, access_key):
        # Initial connect to DME TCP
        self._logger.info("Connecting to dme world Stage [1] ...")
        pkt = bytes_from_hex('156B00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += bytes_from_hex('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += access_key

        self.queue(pkt)

        # wait half a second
        await asyncio.sleep(self._wait_time_for_packets)

        # Check the result
        data = self.dequeue()
        if data[0] != 0x07:
            raise Exception('Unknown response!')
        self._player_id = bytes_to_int_little(data[6:8])
        self._player_count = bytes_to_int_little(data[8:10])

        data = self.dequeue()
        if data[0] != 0x18: # we can ignore this
            raise Exception('Unknown response!')

        self._logger.info(f"Connected Stage [1]! Player ID: {self._player_id} | Player count: {self._player_count}")

    def get_player_id(self):
        return self._player_id

    def get_player_count(self):
        return self._player_count