
import logging
logger = logging.getLogger('thug.model.bot4')
logger.setLevel(logging.INFO)

from datetime import datetime

from model.bots.prototype import prototype
from medius.dme_packets import *

import asyncio

import random
class bot4(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.arsenal.weapons['flux']['hit_rate'] = 1
        self.arsenal.weapons['rocket']['hit_rate'] = 1
        self.arsenal.weapons['grav']['hit_rate'] = 1
        self.arsenal.weapons['n60']['hit_rate'] = 1


        ###### Set the cycle
        weapon_order = list(self.game_state.weapons)
        random.shuffle(weapon_order)
        weapon_order_map = {}

        if len(weapon_order) == 0:
            pass
        elif len(weapon_order) == 1:
            weapon_order_map[weapon_order[0]] = weapon_order[0]
        else:
            for i in range(len(weapon_order)-1):
                weapon_order_map[weapon_order[i]] = weapon_order[i+1]
            weapon_order_map[weapon_order[-1]] = weapon_order[0]
        self.weapon_order_map = weapon_order_map

        self.changing_weapons = False

    def __str__(self):
        return "bot4"

    def posthook_weapon_fired(self):
        if self.changing_weapons == False:
            self._model._loop.create_task(self.change_weapon_timer())

    async def change_weapon_timer(self):
        self.changing_weapons = True
        await asyncio.sleep(.3)
        self.change_weapon()
        self.changing_weapons = False

    def change_weapon(self):
        self.weapon_switch_dt = datetime.now().timestamp()

        if self.game_state.weapons == []:
            weapon = 'wrench'
        elif len(self.game_state.weapons) == 1 or self.game_state.player.weapon == None:
            weapon = random.choice(self.game_state.weapons)
        else:
            weapon = self.weapon_order_map[self.game_state.player.weapon]

        self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': weapon}})])
        self.game_state.player.weapon = weapon
