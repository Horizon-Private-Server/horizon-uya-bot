import asyncio
from queue import Queue
import sys

from utils.utils import *
from utils.rtbufferdeframer import RtBufferDeframer

class AbstractUdp:
    def __init__(self, loop, config, ip: str, port: int):
        self.loop = loop
        self._logger = None

        self._config = config
        self._wait_time_for_packets = config['wait_time_for_packets']

        self._deframer = RtBufferDeframer()

        self._ip = ip
        self._port = port

        self.transport = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001

    def connection_made(self, transport):
        self.transport = transport

    async def start(self):
        await self.loop.create_datagram_endpoint(lambda: self, remote_addr=(self._ip, self._port))

    def datagram_received(self, data, addr):
        if data == b'':
            self._logger.info("Disconnected by server!")
            sys.exit()

        packets = self._deframer.deframe([data])

        for packet in packets:
            self._logger.debug(f"I | {bytes_to_hex(packet)}")
            if packet[0] not in [0x05]: # 05 = echo, 07 = connected, 18 =
                self._read_queue.put(packet)

    async def write(self):
        while True:
            size = self._write_queue.qsize()

            if size != 0:
                final_data = b''
                for i in range(size):
                      final_data += self._write_queue.get()
                self._logger.debug(f"O | {bytes_to_hex(final_data)}")
                self.transport.sendto(final_data, (self._ip, self._port))
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        while True:
            self._write_queue.put(hex_to_bytes('050100A5'))
            await asyncio.sleep(30)

    def queue(self, data: bytes):
        self._write_queue.put(data)

    def dequeue(self):
        return self._read_queue.get()
