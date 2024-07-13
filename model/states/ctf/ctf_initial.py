
from model.states.state import State
from butils.utils import *

class ctf_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        pass

    def update(self):
        # If we have no enemies, just capture!
        if self.state_machine.game_state.no_enemies_in_game:
            # Move to rush_capture
            self.state_machine.transition_state('ctf_rush_grab_flag', {})

        