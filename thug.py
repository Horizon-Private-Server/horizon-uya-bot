
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

from model.model import Model

import requests
import json


config = {
    'account_id': 50005,
    'username': 'CPU-001',
    'world_id': 0,
    'skin': 'robo rooster',
    'bolt': 4,
    'clan_tag': '',
    'team': 'blue',
    'autojoin': 'True',
    'session_key': '3A634A7E8B898C71\x00',
    'mls_ip': '54.189.126.108', 'mls_port': 10078,
    'dmetcp_ip': '54.189.126.108', 'dmetcp_port': 10079,
    'dmeudp_ip': '54.189.126.108', 'dmeudp_port': 51000,
}

class Thug:
    def __init__(self, config: dict):
        logger.info("Initializing ...")
        self.loop = asyncio.get_event_loop()

        self._config = config

        # For debugging so we don't have to change the world id every time
        if self._config['autojoin'] == 'True':
            world_id = json.loads(requests.get(f'http://{self._config["mls_ip"]}:8281/robo/games').text)[-1]['dme_world_id']
            self._config['world_id'] = world_id

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

        self._model = Model(self._config, self.loop, self._tcp_conn, self._udp_conn)

        #self.loop.create_task(self._tcp_conn.main(self._model))
        #self.loop.create_task(self._udp_conn.main(self._model))
        self.loop.create_task(self._udp_conn.main(self._model))
        self.loop.run_until_complete(self._tcp_conn.main(self._model))


Thug(config)
