import os
import asyncio
import logging

logger = logging.getLogger('thug')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

from butils.utils import *

import time
import sys

from connections.mastcp import MasTcp
from connections.mlstcp import MlsTcp
from connections.dmetcp import DmeTcp
from connections.dmeudp import DmeUdp

from model.model import Model

import requests
import json

from constants.constants import SKIN_MAP

import random
from datetime import datetime

class Thug:
    def __init__(self, config:dict):
        logger.info("Initializing ...")
        self._config = config

        self._config['start_time'] = datetime.now().timestamp()

        self.loop = asyncio.get_event_loop()

        if self._config['skin'] == 'random':
            skins = list(SKIN_MAP.values())
            skins.remove('NA')
            random.shuffle(skins)
            self._config['skin'] = skins[0]

        # For debugging so we don't have to change the world id every time
        # if self._config['autojoin'] == 'True':
        #     world_id = json.loads(requests.get(f'http://{self._config["mls_ip"]}:8281/robo/games').text)[-1]['dme_world_id']
        #     self._config['world_id'] = world_id

        logger.info(self._config)

        self._mas_conn = MasTcp(self.loop, self._config, self._config['mas_ip'], self._config['mas_port'])

        # Initialize connections
        # logger.info("Initializing MLS ... ")
        # self._mls_conn = MlsTcp(self.loop, self._config, self._config['mls_ip'], self._config['mls_port'])
        # logger.info("Initializing DME TCP ...")
        # self._tcp_conn = DmeTcp(self.loop, self._config, self._config['dmetcp_ip'], self._config['dmetcp_port'])
        # logger.info("Initializing DME UDP ...")
        # self._udp_conn = DmeUdp(self.loop, self._config, self._config['dmeudp_ip'], self._config['dmeudp_port'])




        # Connect to DME world
        # access_key = self._mls_conn.get_access_key()
        # self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_1(access_key))
        # self.loop.run_until_complete(self._udp_conn.connect_to_dme_world(self._tcp_conn.get_player_id()))
        # self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_2())

        # self._model = Model(self._config, self.loop, self._tcp_conn, self._udp_conn)

        # self.loop.create_task(self._udp_conn.main(self._model))
        # self.loop.run_until_complete(self._tcp_conn.main(self._model))

def read_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        return json.loads(f.read())

def read_config_from_env():
    return {
        "bot_class":os.getenv("BOT_CLASS"),
        "account_id":int(os.getenv("ACCOUNT_ID")),
        "username":os.getenv("USERNAME"),
        "world_id":int(os.getenv("WORLD_ID")),
        "skin":os.getenv("SKIN"),
        "bolt":int(os.getenv("BOLT")),
        "clan_tag":os.getenv("CLAN_TAG"),
        "team":os.getenv("TEAM"),
        "autojoin":os.getenv("AUTOJOIN"),
        "session_key":os.getenv("SESSION_KEY"),
        "mls_ip":os.getenv("MLS_IP"),
        "mls_port":int(os.getenv("MLS_PORT")),
        "dmetcp_ip":os.getenv("DMETCP_IP"),
        "dmetcp_port":int(os.getenv("DMETCP_PORT")),
        "dmeudp_ip":os.getenv("DMEUDP_IP"),
        "dmeudp_port":int(os.getenv("DMEUDP_PORT")),
        "timeout":float(os.getenv("TIMEOUT"))
    }

# AWS Lambda handler
def handler(event, context):
    print(event)
    try:
        Thug(config = event)
    except:
        logger.exception("Thug error!")
        return 1
    return 0

if __name__ == '__main__':
    if os.getenv('USE_ENV_VARS') == 'Yes':
        Thug(config=read_config_from_env())
    else:
        Thug(config = read_config())
