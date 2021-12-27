import asyncio
from queue import Queue
import sys

from utils import *

import logging
logger = logging.getLogger('thug.mlstcp')

class MlsTcp:
    def __init__(self, loop, config, ip: str, port: int):
        self._loop = loop

        self._config = config

        self._ip = ip
        self._port = port

        self._access_key = None

        self._reader = None
        self._writer = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001

        self._loop.run_until_complete(self.start())
        self._loop.create_task(self.read())
        self._loop.create_task(self.write())
        self._loop.run_until_complete(self.generate_access_key())
        self._loop.create_task(self.echo())
        self._loop.run_until_complete(self.connect_to_mls())


    async def start(self):
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)

    async def generate_access_key(self):
        message = bytes_from_hex("0BC60001F331000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        self.queue(message)

        # wait half a second
        await asyncio.sleep(.1)

        # Check the result
        data = self.dequeue()
        if data == b'':
            logger.info("Disconnected by server!")
            sys.exit()

        self._access_key = data[174:]

    async def connect_to_mls(self):
        pkt = bytes_from_hex('006B000108010000BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

        logger.info(f"Sending MLS initial connect: {bytes_to_hex(pkt)}")

        self.queue(pkt)

    async def read(self):
        while True:
            data = await self._reader.read(500)
            if data == b'':
                logger.info("Disconnected by server!")
                sys.exit()
            logger.debug(f"I | {data}")
            self._read_queue.put(data)
            await asyncio.sleep(self._readwrite_time)

    async def write(self):
        while True:
            size = self._write_queue.qsize()
                
            if size != 0:
                final_data = b''
                for i in range(size):
                    final_data += self._write_queue.get()
                logger.debug(f"O | {final_data}")
                self._writer.write(final_data)
                await self._writer.drain()
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        while True:
            self._write_queue.put(bytes_from_hex('050100A5'))
            await asyncio.sleep(30)

    def queue(self, data: bytes):
        self._write_queue.put(data)

    def dequeue(self):
        return self._read_queue.get()
