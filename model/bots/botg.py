
import logging
logger = logging.getLogger('thug.model.botg')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class botg(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.game_state.player._default_health = 1000
        self.game_state.player.reset_health()
        self._weapons_enabled = True

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
