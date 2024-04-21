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
from utils.localapi import LocalApi

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

        if self._config.skin == 'random':
            skins = list(SKIN_MAP.values())
            skins.remove('NA')
            random.shuffle(skins)
            self._config.skin = skins[0]

        self._config.start_time = datetime.now()
        self._loop_time = .001

        self.loop = asyncio.new_event_loop()

        self._network_manager = NetworkManager(self.loop, self._config)

        self._timer = TimeoutTimer(self.loop, self._config.start_time, self._config.timeout)

        self._model = Model(self.loop, 
                            self._network_manager, 
                            self._network_manager._mls.gameinfo, 
                            config.bot_class,
                            config.account_id, 
                            self._network_manager._dmetcp.player_id, 
                            config.team, 
                            config.username,
                            config.skin,
                            config.clan_tag,
                            config.bolt
                            )
        
            # Set local API for remote injection of packets
        self.local_api = LocalApi(self.loop, self._model, self._config.account_id) if self._config.local else None

        self.loop.run_until_complete(self.main())


    async def main(self):
        while self.is_alive():
            await asyncio.sleep(5)

        logger.info("Ending main routine!")
        await self._timer.kill()
        await self._network_manager.kill()
        await self._model.kill()
        if self.local_api:
            await self.local_api.kill()

        await asyncio.sleep(30)

        logger.info("Thug finished.")

    def is_alive(self):
        # Check if we have fully timed out
        return self._timer.alive and self._network_manager.is_alive() and self._model.alive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Horizon's UYA Bot. (Thug)")
    parser.add_argument('--config', type=str, default=None, help='Path to JSON configuration file (default: use ENV Vars)')

    args = parser.parse_args()

    # Load configuration from the specified JSON file
    config_file = args.config
    config = Config(args.config)

    Thug(config=config)

