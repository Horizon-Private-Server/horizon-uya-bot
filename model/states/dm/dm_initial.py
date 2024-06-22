
from model.states.state import State
from butils.utils import *

class dm_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        pass

    def update(self):
        self.state_machine.target = self.state_machine.game_state.players[0].coord


