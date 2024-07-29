
from model.states.state import State
from model.states.ctf.ctf_main import ctf_main
from butils.utils import *

class ctf_engage(ctf_main):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        super().enter(msg)

    def update(self):
        # Get whether to rush/def/mid 
        state = self.state_machine.game_state.ctf_get_objective()
        if state != 'engage':
            self.state_machine.transition_state('ctf_initial', {})
            return

        self.engage()