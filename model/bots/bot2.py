
import logging
logger = logging.getLogger('thug.model.bot2')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot2(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self._fire_rate = {
            'n60': .1,
            'rocket': .007,
            'flux': .007,
            'blitz': .007,
            'grav': .007
        }
        self._hit_rate = {
            'n60': .3,
            'rocket': .3,
            'flux': .3,
            'blitz': .3,
            'grav': .3
        }

    def __str__(self):
        return "bot2"
