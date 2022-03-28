
import logging
logger = logging.getLogger('thug.model.bot3')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot3(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

    def __str__(self):
        return "bot3"
