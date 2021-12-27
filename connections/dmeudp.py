import asyncio
import logging

from utils import *
from connections.abstractudp import AbstractUdp

class DmeUdp(AbstractUdp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.dmeudp')
        self._logger.setLevel(logging.DEBUG)

        self.loop.create_task(self.start())
        self.loop.run_until_complete(asyncio.sleep(1))
        self.loop.create_task(self.write())
        self.loop.create_task(self.echo())

    async def connect_to_dme_world(self):
        pass