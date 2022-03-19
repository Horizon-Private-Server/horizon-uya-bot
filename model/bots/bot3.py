
import logging
logger = logging.getLogger('thug.model.bot3')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot3(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self._fire_rate = {
            'n60': .1,
            'rocket': .01,
            'flux': .01,
            'blitz': .01,
            'grav': .01
        }
        self._hit_rate = {
            'n60': .6,
            'rocket': .6,
            'flux': .6,
            'blitz': .6,
            'grav': .6
        }

    def __str__(self):
        return "bot3"
