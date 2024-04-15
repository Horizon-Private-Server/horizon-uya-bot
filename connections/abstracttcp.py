import asyncio
from queue import Queue
import sys
from datetime import datetime

from butils.utils import *
from butils.rtbufferdeframer import RtBufferDeframer

class AbstractTcp:
    def __init__(self, loop, ip: str, port: int):
        self.alive = True
        self._logger = None
        self.loop = loop

        self._ip = ip
        self._port = port

        self._deframer = RtBufferDeframer()

        self._reader = None
        self._writer = None

        self._read_queue = Queue()
        self._write_queue = Queue()

        self._readwrite_time = 0.0001

        self._last_echo_sent = datetime.now()
        self._last_echo_recv = datetime.now()
        

    async def start(self):
        self._logger.debug("Starting async open_connection ...")
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)
        self._logger.debug("Done async open_connection ...")
        self._logger.debug("Connection opened!")
        self.loop.create_task(self.read_data())
        self.loop.create_task(self.write_data())

    async def read_data(self):
        self._logger.debug("Starting read data ...")
        while self.alive:
            data = await self._reader.read(500)
            if data == b'':
                await asyncio.sleep(self._readwrite_time)
                continue
                # self._logger.info("Disconnected by server!")
                # sys.exit()

            packets = self._deframer.deframe([data])

            for packet in packets:
                self._logger.debug(f"I | {bytes_to_hex(packet)}")


                if packet[0] == 0x05:
                    self._last_echo_recv = datetime.now()
                else:  # 05 = echo, 07 = connected, 18 =
                    self._read_queue.put(packet)


            await asyncio.sleep(self._readwrite_time)

    async def write_data(self):
        self._logger.debug("Starting write data ...")
        while self.alive:
            size = self._write_queue.qsize()

            if size != 0:
                final_data = b''
                for i in range(size):
                    if len(final_data) > 300:
                        self._logger.debug(f"O | {bytes_to_hex(final_data)}")
                        self._writer.write(final_data)
                        await self._writer.drain()
                        final_data = b''

                    final_data += self._write_queue.get()

                if final_data != b'':
                    self._logger.debug(f"O | {bytes_to_hex(final_data)}")
                    self._writer.write(final_data)
                    await self._writer.drain()
                    
            await asyncio.sleep(self._readwrite_time)

    async def echo(self):
        self._logger.info("Starting echo co-routine ...")
        while self.alive:

            # If we haven't gotten a response since the last ping, force close
            if self._last_echo_recv == None:
                self._logger.info("Force closing connection, no echo received!")
                await self.close()

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
    


    async def close(self):
        await asyncio.wait_for(self._close(), timeout=5.0)

    async def _close(self):
        self._logger.info("Closing connections ...")
        self.alive = False
        self._writer.close()
        await self._writer.wait_closed()        
        self._logger.info("Connections closed!")

