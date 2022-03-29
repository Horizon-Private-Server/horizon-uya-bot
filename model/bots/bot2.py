
import logging
logger = logging.getLogger('thug.model.bot2')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot2(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.arsenal.weapons['flux']['shoot_rate'] = 1
        self.arsenal.weapons['rocket']['shoot_rate'] = 1
        self.arsenal.weapons['grav']['shoot_rate'] = 1
        self.arsenal.weapons['n60']['shoot_rate'] = 1

        self.arsenal.weapons['flux']['hit_rate'] = .5
        self.arsenal.weapons['rocket']['hit_rate'] = .5
        self.arsenal.weapons['grav']['hit_rate'] = .5
        self.arsenal.weapons['n60']['hit_rate'] = .5

    def __str__(self):
        return "bot2"
