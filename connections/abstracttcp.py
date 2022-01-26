import asyncio
from queue import Queue
import sys

from utils.utils import *
from utils.rtbufferdeframer import RtBufferDeframer

class AbstractTcp:
    def __init__(self, loop, config, ip: str, port: int):
        self._logger = None
        self.loop = loop

        self._config = config

        self._wait_time_for_packets = config['wait_time_for_packets']
        self._ip = ip
        self._port = port

        self._deframer = RtBufferDeframer()

        self._reader = None
        self._writer = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001

    async def start(self):
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)

    async def read(self):
        while True:
            data = await self._reader.read(500)
            if data == b'':
                self._logger.info("Disconnected by server!")
                sys.exit()

            packets = self._deframer.deframe([data])

            for packet in packets:
                self._logger.debug(f"I | {bytes_to_hex(packet)}")


                if packet[0] not in [0x05]:  # 05 = echo, 07 = connected, 18 =
                    self._read_queue.put(packet)

            await asyncio.sleep(self._readwrite_time)

    async def write(self):
        while True:
            size = self._write_queue.qsize()

            if size != 0:
                final_data = b''
                for i in range(size):
                    final_data += self._write_queue.get()
                self._logger.debug(f"O | {bytes_to_hex(final_data)}")
                self._writer.write(final_data)
                await self._writer.drain()
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        self._logger.info("Starting echo co-routine ...")
        while True:
            self._write_queue.put(hex_to_bytes('050100A5'))
            await asyncio.sleep(30)

    def queue(self, data: bytes):
        self._write_queue.put(data)

    def dequeue(self):
        if self._read_queue.qsize() == 0:
            return None
        return self._read_queue.get()

    def qsize(self):
        return self._read_queue.qsize()
