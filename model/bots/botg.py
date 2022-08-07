
import logging
logger = logging.getLogger('thug.model.botg')
logger.setLevel(logging.INFO)

import random
import asyncio

from datetime import datetime

from model.bots.prototype import prototype

from butils.utils import *


class botg(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.follow_player = True

        self.game_state.player._default_health = 1000
        self.game_state.player.reset_health()
        self._weapons_enabled = True

        self.changing_weapons = False

        self.firing = True

        self.arsenal.weapons['flux']['shoot_rate'] = 1
        self.arsenal.weapons['rocket']['shoot_rate'] = 1
        self.arsenal.weapons['grav']['shoot_rate'] = 1
        self.arsenal.weapons['n60']['shoot_rate'] = 1

        self.arsenal.weapons['flux']['hit_rate'] = 1
        self.arsenal.weapons['rocket']['hit_rate'] = 1
        self.arsenal.weapons['grav']['hit_rate'] = 1
        self.arsenal.weapons['n60']['hit_rate'] = 1

        self.arsenal.weapons['flux']['cooldown'] = .01
        self.arsenal.weapons['rocket']['cooldown'] = .01
        self.arsenal.weapons['grav']['cooldown'] = .01
        self.arsenal.weapons['n60']['cooldown'] = .01

        self._model.game_state.map.cboot_factor = 2
        self._model.game_state.map.cboot_distance = 100

        self._model._loop.create_task(self.cycle())

    def __str__(self):
        return "botg"

    def objective(self):
        # first determine the state of the flag etc

        # update angle/coord
        if not self.game_state.player.is_dead:
            if self.game_state.player.movement_packet_num % 4 == 0:

                self.tracking = self._model.get_closest_enemy_player()

                # Follow
                #new_coord = self.game_state.map.path(self.game_state.player.coord, self.tracking.coord)

                # Strafe and get coordinate that is close to this one, but in a random direction
                new_coord = self.game_state.map.get_random_coord_connected_close(self.game_state.player.coord, self.tracking.coord)

                if new_coord[2] > self.game_state.player.coord[2]:
                    self.game_state.player.animation = 'jump'
                elif random.random() < .2:
                    self.game_state.player.animation = 'jump'
                elif new_coord != self.game_state.player.coord:
                    self.game_state.player.animation = 'forward'
                else:
                    self.game_state.player.animation = None

                self.game_state.player.coord = new_coord

        # Update camera angle
        if self.game_state.player.movement_packet_num % 5 == 0:
            self.game_state.player.x_angle = calculate_angle(self.game_state.player.coord, self.tracking.coord)

        # Fire weapon
        if self.firing:
            self.fire_weapon()

    # def posthook_weapon_fired(self):
    #     start_ts = self._model._config['start_time']
    #     t = datetime.now().timestamp()
    #     minute_diff = ((t - start_ts) / 60)
    #
    #     if minute_diff > 1: # after 1 min, start cycling
    #         if self.changing_weapons == False:
    #             self._model._loop.create_task(self.change_weapon_timer())

    async def cycle(self):
        while self._model.alive:
            time_to_sleep = random.random() * 3 + 2
            self.firing = False
            await asyncio.sleep(1.25)
            self.firing = True
            await asyncio.sleep(time_to_sleep)
            self.change_weapon()
