
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

    def __str__(self):
        return "botg"
