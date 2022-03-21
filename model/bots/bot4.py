
import logging
logger = logging.getLogger('thug.model.bot4')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot4(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self._fire_rate = {
            'n60': .15,
            'rocket': .03,
            'flux': .03,
            'blitz': .03,
            'grav': .03
        }
        self._hit_rate = {
            'n60': .9,
            'rocket': .9,
            'flux': .9,
            'blitz': .9,
            'grav': .9
        }

    def __str__(self):
        return "bot4"

    def fire_weapon(self):
        super().fire_weapon()
        self.change_weapon()
