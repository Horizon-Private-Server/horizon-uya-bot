
import logging
logger = logging.getLogger('thug.model.bot4')
logger.setLevel(logging.INFO)

from datetime import datetime

from model.bots.prototype import prototype
from medius.dme_packets import *
from butils.circularlist import CircularList

import asyncio

import random
class cpu4(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.arsenal.weapons['flux']['hit_rate'] = .2
        self.arsenal.weapons['grav']['hit_rate'] = .3

        ###### Set the cycle
        weapon_order_list = list(self.game_state.weapons)
        random.shuffle(weapon_order_list)
        if set(weapon_order_list) == {'blitz', 'flux', 'grav'}:
            weapon_order_list = ['grav', 'flux', 'blitz']
        self.weapon_order = CircularList(weapon_order_list, circular=True, casttype=str)


    def objective(self):
        logger.info(str(self.model.game_state))
        logger.info(str(self.model.game_state.object_manager))

        self.target = self.game_state.players[0].coord


        self.game_state.player.coord = [28009, 56248, 7413]

        # Quad patrol near red base marcadia
        marc_points = [
            [32939, 54784, 7413],
            [32418, 53872, 7413],
            [31608, 54666, 7413],
            [32540, 55641, 7407],
        ]

        # Moving across map by healthboxes marcadia
        # marc_points = [
        #     [33289, 56515, 7413],
        #     [30680, 56370, 7413],
        #     [27973, 56516, 7413],
        # ]

        #self.patrol(marc_points, circular=False)

        #self.fire_weapon(object_id = self.game_state.players[0].player_id)


    def __str__(self):
        return "cpu4"
