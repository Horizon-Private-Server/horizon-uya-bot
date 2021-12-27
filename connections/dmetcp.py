import asyncio
from queue import Queue
import sys

from utils import *
from rtbufferdeframer import RtBufferDeframer

import logging
logger = logging.getLogger('thug.dmetcp')

class DmeTcp:
    def __init__(self, loop, config, ip: str, port: int):
        self._loop = loop
        self._config = config

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

    def connect_to_staging(self):
        self._loop.run_until_complete(self.connect_to_staging_tcp())

    async def connect_to_staging_tcp(self):
        # Initial connect to DME TCP
        pkt = bytes_from_hex('156B00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += bytes_from_hex('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

        logger.info(f"Sending: {bytes_to_hex(pkt)}")

        self.queue(pkt)

        # wait half a second
        await asyncio.sleep(.5)

        # Check the result
        data = self.dequeue()
        if data[0] != 0x07:
            # TODO: PARSE THIS TO GET player count, dme player id
            raise Exception('Unknown response!')
        data = self.dequeue()
        if data[0] != 0x18:
            raise Exception('Unknown response!')

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
                    logger.debug(f"I | {packet}")

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
