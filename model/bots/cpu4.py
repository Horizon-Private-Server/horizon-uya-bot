
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

        self.arsenal.weapons['flux']['hit_rate'] = 1
        self.arsenal.weapons['rocket']['hit_rate'] = 1
        self.arsenal.weapons['grav']['hit_rate'] = 1
        self.arsenal.weapons['n60']['hit_rate'] = 1


        ###### Set the cycle
        weapon_order_list = list(self.game_state.weapons)
        random.shuffle(weapon_order_list)
        if set(weapon_order_list) == {'blitz', 'flux', 'grav'}:
            weapon_order_list = ['grav', 'flux', 'blitz']
        self.weapon_order = CircularList(weapon_order_list, circular=True, casttype=str)



    def objective(self):

        self.target = self.game_state.players[0].coord

        marc_points = [
            [32939, 54784, 7413],
            [32418, 53872, 7413],
            [31608, 54666, 7413],
            [32540, 55641, 7407],
        ]


        self.patrol(marc_points, circular=False)

        self.fire_weapon()


    def __str__(self):
        return "cpu4"

