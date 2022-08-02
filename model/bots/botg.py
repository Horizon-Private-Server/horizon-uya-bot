
import logging
logger = logging.getLogger('thug.model.botg')
logger.setLevel(logging.INFO)

import asyncio

from datetime import datetime

from model.bots.prototype import prototype

class botg(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.follow_player = True

        self.game_state.player._default_health = 1000
        self.game_state.player.reset_health()
        self._weapons_enabled = True

        self.changing_weapons = False

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

    def __str__(self):
        return "botg"

    def posthook_weapon_fired(self):
        start_ts = self._model._config['start_time']
        t = datetime.now().timestamp()
        minute_diff = ((t - start_ts) / 60)

        if minute_diff > 7: # after 7 min, start cycling
            if self.changing_weapons == False:
                self._model._loop.create_task(self.change_weapon_timer())

    async def change_weapon_timer(self):
        self.changing_weapons = True
        await asyncio.sleep(.3)
        self.change_weapon()
        self.changing_weapons = False
