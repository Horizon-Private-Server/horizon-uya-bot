
import logging
logger = logging.getLogger('thug.model.bot0')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot0(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.follow_player = True

        self._weapons_enabled = False

    def __str__(self):
        return "bot0"
