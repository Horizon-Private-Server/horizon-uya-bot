import os
import asyncio
import logging
import argparse

logger = logging.getLogger('thug')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

from butils.utils import *

from utils.timeouttimer import TimeoutTimer
from utils.config import Config

import time
import sys

from connections.networkmanager import NetworkManager

from model.model import Model

import json

from constants.constants import SKIN_MAP

import random
from datetime import datetime


class Thug:
    def __init__(self, config:dict):
        logger.info("Initializing ...")
        self._config = config

        self._config.start_time = datetime.now()
        self._loop_time = .001

        self.loop = asyncio.new_event_loop()

        self._timer = TimeoutTimer(self.loop, self._config.start_time, self._config.timeout)
        self._network_manager = NetworkManager()

        if self._config.skin == 'random':
            skins = list(SKIN_MAP.values())
            skins.remove('NA')
            random.shuffle(skins)
            self._config.skin = skins[0]

        logger.info(self._config)


        self.loop.run_until_complete(self.main())
        return

        self.loop.run_until_complete(self._tcp_conn.main(self._model))

        logger.info("Initializing MAS ... ")
        self._mas_conn = MasTcp(self.loop, self._config, self._config['mas_ip'], self._config['mas_port'])
        self.loop.run_until_complete(self._mas_conn.close())

        # Initialize connections
        logger.info("Initializing MLS ... ")
        self._mls_conn = MlsTcp(self.loop, self._config, self._mas_conn._session_key, self._mas_conn._access_key, self._config['mls_ip'], self._config['mls_port'])
        logger.info("Initializing DME TCP ...")
        self._tcp_conn = DmeTcp(self.loop, self._config)

        self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_1())
        
        logger.info("Initializing DME UDP ...")
        self._udp_conn = DmeUdp(self.loop, self._config, self._config['dmeudp_ip'], self._config['dmeudp_port'])

        # Connect to DME world
        self.loop.run_until_complete(self._udp_conn.connect_to_dme_world(self._tcp_conn.get_player_id()))
        self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_2())



        self._model = Model(self._config, self.loop, self._tcp_conn, self._udp_conn)

        self.loop.create_task(self._udp_conn.main(self._model))
        self.loop.run_until_complete(self._tcp_conn.main(self._model))


    async def main(self):
        while self.is_alive():
            #logger.info("Looping!")

            await self._network_manager.update()

            await asyncio.sleep(self._loop_time)

        logger.info("Ending main routine!")
        await self._timer.kill()

        logger.info("Thug finished.")

    def is_alive(self):
        # Check if we have fully timed out
        return self._timer.alive and self._network_manager.alive
        

        # Check if the network manager has timed out

        # Check if the model quit

        return False









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
    parser = argparse.ArgumentParser(description="Run Horizon's UYA Bot. (Thug)")
    parser.add_argument('--config', type=str, default=None, help='Path to JSON configuration file (default: use ENV Vars)')

    args = parser.parse_args()

    # Load configuration from the specified JSON file
    config_file = args.config
    config = Config(args.config)

    Thug(config=config)

