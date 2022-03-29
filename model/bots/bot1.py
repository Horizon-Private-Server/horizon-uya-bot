
import logging
logger = logging.getLogger('thug.model.bot1')
logger.setLevel(logging.INFO)

from model.bots.prototype import prototype

class bot1(prototype):
    def __init__(self, model, game_state):
        super().__init__(model, game_state)

        self.arsenal.weapons['flux']['shoot_rate'] = .6
        self.arsenal.weapons['rocket']['shoot_rate'] = .6
        self.arsenal.weapons['grav']['shoot_rate'] = .6
        self.arsenal.weapons['n60']['shoot_rate'] = .6

        self.arsenal.weapons['flux']['hit_rate'] = .25
        self.arsenal.weapons['rocket']['hit_rate'] = .25
        self.arsenal.weapons['grav']['hit_rate'] = .25
        self.arsenal.weapons['n60']['hit_rate'] = .25

    def __str__(self):
        return "bot1"
