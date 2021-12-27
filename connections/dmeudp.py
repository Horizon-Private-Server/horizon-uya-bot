import asyncio
from queue import Queue
import time

from utils import *
from rtbufferdeframer import RtBufferDeframer

import logging
logger = logging.getLogger('thug.dmeudp')

class DmeUdp:
    def __init__(self, loop, ip: str, port: int):
        self._loop = loop

        self._deframer = RtBufferDeframer()

        self._ip = ip
        self._port = port
        
        self.transport = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001
        self._loop.create_task(self.start())
        self._loop.run_until_complete(asyncio.sleep(1))
        self._loop.create_task(self.write())
        self._loop.create_task(self.echo())

    def connection_made(self, transport):
        self.transport = transport

    async def start(self):
        await self._loop.create_datagram_endpoint(lambda: self, remote_addr=(self._ip, self._port))

    def datagram_received(self, data, addr):
        logger.debug(f"RECV:  {data.hex().upper()}")
        if data == b'':
            logger.info("Disconnected by server!")
            sys.exit()

        packets = self._deframer.deframe([data])

        for packet in packets:
            logger.debug(f"Read: {packet}")
            if packet[0] not in [0x05]: # 05 = echo, 07 = connected, 18 = 
                self._read_queue.put(packet)

    async def write(self):
        while True:
            size = self._write_queue.qsize()
                
            if size != 0:
                final_data = b''
                for i in range(size):
                      final_data += self._write_queue.get()
                logger.debug(f"Writing: {final_data}")
                self.transport.sendto(final_data, (self._ip, self._port))
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        while True:
            self._write_queue.put(bytes_from_hex('050100A5'))
            await asyncio.sleep(30)

    def queue(self, data: bytes):
        self._write_queue.put(data)

    def dequeue(self):
        return self._read_queue.get()
