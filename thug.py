
import asyncio
import logging

logger = logging.getLogger('thug')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

from utils.utils import *

import time
import sys

from connections.mlstcp import MlsTcp
from connections.dmetcp import DmeTcp
from connections.dmeudp import DmeUdp

config = {
    'account_id': 2,
    'username': 'Thug',
    'world_id': 1,
    'session_key': '18D5C0F0799F6F69\x00',
    'mls_ip': '127.0.0.1', 'mls_port': 10078,
    'dmetcp_ip': '127.0.0.1', 'dmetcp_port': 10079,
    'dmeudp_ip': '127.0.0.1', 'dmeudp_port': 51000,
    'wait_time_for_packets': .1
}

class Thug:
    def __init__(self, config: dict):
        logger.info("Initializing ...")
        self.loop = asyncio.get_event_loop()

        self._config = config

        # Initialize connections
        logger.info("Initializing MLS ... ")
        self._mls_conn = MlsTcp(self.loop, config, config['mls_ip'], config['mls_port'])
        logger.info("Initializing DME TCP ...")
        self._tcp_conn = DmeTcp(self.loop, config, config['dmetcp_ip'], config['dmetcp_port'])
        logger.info("Initializing DME UDP ...")
        self._udp_conn = DmeUdp(self.loop, config, config['dmeudp_ip'], config['dmeudp_port'])

        # Connect to DME world
        access_key = self._mls_conn.get_access_key()
        self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_1(access_key))
        self.loop.run_until_complete(self._udp_conn.connect_to_dme_world(self._tcp_conn.get_player_id()))
        self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_2())

        self.loop.create_task(self._tcp_conn.lobby_routine())

        self.loop.run_forever()

Thug(config)
