
import asyncio
import logging

logger = logging.getLogger('thug')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

from utils import *

import time
import sys

from connections.mlstcp import MlsTcp
from connections.dmetcp import DmeTcp
from connections.dmeudp import DmeUdp

config = {
    'account_id': 5,
    'username': 'Thug',
    'world_id': 1,
    'session_key': 'EC064833A70D5F70\x00',
    'mls_ip': '127.0.0.1', 'mls_port': 10078,
    'dmetcp_ip': '127.0.0.1', 'dmetcp_port': 10079,
    'dmeudp_ip': '127.0.0.1', 'dmeudp_port': 51000
}

class Thug:
    def __init__(self, config: dict):
        self.loop = asyncio.get_event_loop()

        self._config = config

        # Connection status
        self.loop.run_until_complete(self._generate_access_key())
        self._mls_conn = MlsTcp(self.loop, config['mls_ip'], config['mls_port'])
        self.loop.run_until_complete(self.connect_to_mls())

        self.loop.run_until_complete(self._generate_access_key())
        self._tcp_conn = DmeTcp(self.loop, config['dmetcp_ip'], config['dmetcp_port'])
        self._udp_conn = DmeUdp(self.loop, config['dmeudp_ip'], config['dmeudp_port'])

        self.loop.run_until_complete(self.connect_to_staging_tcp())
        self.loop.run_until_complete(self.connect_to_staging_udp())

        self.loop.run_forever()

    async def connect_to_mls(self):
        pkt = bytes_from_hex('006B000108010000BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

        logger.info(f"Sending MLS initial connect: {bytes_to_hex(pkt)}")

        self._mls_conn.queue(pkt)

    async def connect_to_staging_tcp(self):
        # Initial connect to DME TCP
        pkt = bytes_from_hex('156B00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += bytes_from_hex('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

        logger.info(f"Sending: {bytes_to_hex(pkt)}")

        self._tcp_conn.queue(pkt)

        # wait half a second
        await asyncio.sleep(.5)

        # Check the result
        data = self._tcp_conn.dequeue()
        if data[0] != 0x07:
            # TODO: PARSE THIS TO GET player count, dme player id
            raise Exception('Unknown response!')
        data = self._tcp_conn.dequeue()
        if data[0] != 0x18:
            raise Exception('Unknown response!')

    async def connect_to_staging_udp(self):
        while True:
            await asyncio.sleep(10)

    async def _generate_access_key(self):
        reader, writer = await asyncio.open_connection(self._config['mls_ip'], self._config['mls_port'])

        message = bytes_from_hex("0BC60001F331000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        writer.write(message)
        await writer.drain()

        data = await reader.read(500)
        self._access_key = data[174:]
        writer.close()


Thug(config)
