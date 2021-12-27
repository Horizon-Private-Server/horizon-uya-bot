import asyncio
from queue import Queue

from utils import *
from rtbufferdeframer import RtBufferDeframer

import logging
logger = logging.getLogger('thug.dmetcp')

class DmeTcp:
    def __init__(self, loop, ip: str, port: int):
        self._loop = loop

        self._deframer = RtBufferDeframer()

        self._ip = ip
        self._port = port

        self._reader = None
        self._writer = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001
        self._loop.run_until_complete(self.start())
        self._loop.create_task(self.read())
        self._loop.create_task(self.write())
        self._loop.create_task(self.echo())

    async def start(self):
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)

    async def read(self):
        while True:
            if self._reader != None:
                data = await self._reader.read(500)
                if data == b'':
                    logger.info("Disconnected by server!")
                    sys.exit()

                packets = self._deframer.deframe([data])

                for packet in packets:
                    logger.debug(f"Read: {packet}")

                    if packet[0] not in [0x05]: # 05 = echo, 07 = connected, 18 = 
                        self._read_queue.put(packet)

            await asyncio.sleep(self._readwrite_time)

    async def write(self):
        while True:
            size = self._write_queue.qsize()
                
            if size != 0:
                final_data = b''
                for i in range(size):
                      final_data += self._write_queue.get()
                logger.debug(f"Writing: {final_data}")
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
