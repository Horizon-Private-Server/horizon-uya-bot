
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

        self.game_state.player.arsenal.weapons['flux']['hit_rate'] = .3
        self.game_state.player.arsenal.weapons['grav']['hit_rate'] = .2

        ###### Set the cycle
        weapon_order_list = list(self.game_state.weapons)
        random.shuffle(weapon_order_list)
        if set(weapon_order_list) == {'blitz', 'flux', 'grav'}:
            weapon_order_list = ['grav', 'flux', 'blitz']
        self.weapon_order = CircularList(weapon_order_list, circular=True, casttype=str)


    def objective(self):
        logger.info(str(self.model.game_state))
        logger.info(str(self.model.game_state.object_manager))

        target_player_id = 0

        self.target = self.game_state.players[target_player_id].coord

        #self.game_state.player.coord = [32689, 55927, 7413]

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

        self.patrol(marc_points, circular=False)

        self.fire_weapon(object_id = self.game_state.players[target_player_id].player_id)


    def __str__(self):
        return "cpu4"


# func transition_to(target_state_name: String, msg: Dictionary = {}) -> void:
# 	# Safety check, you could use an assert() here to report an error if the state name is incorrect.
# 	# We don't use an assert here to help with code reuse. If you reuse a state in different state machines
# 	# but you don't want them all, they won't be able to transition to states that aren't in the scene tree.
# 	if not has_node(target_state_name):
# 		return

# 	state.exit()
# 	state = get_node(target_state_name)
# 	print("Transitioning to:", state.get_name())
# 	state.enter(msg)
# 	emit_signal("transitioned", state.name)

