
import logging
logger = logging.getLogger('thug.model.bot3')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot3(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.arsenal.weapons['flux']['hit_rate'] = 1
        self.arsenal.weapons['rocket']['hit_rate'] = 1
        self.arsenal.weapons['grav']['hit_rate'] = 1
        self.arsenal.weapons['n60']['hit_rate'] = 1

    def __str__(self):
        return "bot3"
