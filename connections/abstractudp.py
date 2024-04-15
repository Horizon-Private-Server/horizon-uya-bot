import asyncio
from queue import Queue
import sys
from datetime import datetime

from butils.utils import *
from butils.rtbufferdeframer import RtBufferDeframer

class AbstractUdp:
    def __init__(self, loop, ip: str, port: int):
        self.alive = True
        self.loop = loop
        self._logger = None

        self._deframer = RtBufferDeframer()

        self._ip = ip
        self._port = port

        self.transport = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001

        self._last_echo_sent = datetime.now()
        self._last_echo_recv = datetime.now()

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
            if packet[0] == 0x05:
                self._last_echo_recv = datetime.now()
            else: # 05 = echo, 07 = connected, 18 =
                self._read_queue.put(packet)

    async def write(self):
        while self.alive:
            size = self._write_queue.qsize()

            if size != 0:
                final_data = b''
                for i in range(size):
                      final_data += self._write_queue.get()
                self._logger.debug(f"O | {bytes_to_hex(final_data)}")
                self.transport.sendto(final_data, (self._ip, self._port))
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        while self.alive:

            # If we haven't gotten a response since the last ping, force close
            if self._last_echo_recv == None:
                self._logger.info("Force closing connection, no echo received!")
                self.close()

            self._last_echo_sent = datetime.now()
            self._last_echo_recv = None

            self._write_queue.put(hex_to_bytes('050100A5'))
            await asyncio.sleep(15)

    def queue(self, data: bytes):
        self._write_queue.put(data)

    def dequeue(self):
        if self._read_queue.qsize() == 0:
            return None
        return self._read_queue.get()

    def qsize(self):
        return self._read_queue.qsize()

    def close(self):
        self._logger.info("Closing connections ...")
        self.alive = False   
        self._logger.info("Connections closed!")
