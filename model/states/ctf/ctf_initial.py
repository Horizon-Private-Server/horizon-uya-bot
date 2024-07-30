
from model.states.state import State
from butils.utils import *

class ctf_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        pass

    def update(self):

        # Get whether to rush/def/mid 
        state = self.state_machine.game_state.ctf_get_objective()
        if state == 'engage':
            self.state_machine.transition_state('ctf_engage', {})
        elif state == 'rush':
            self.state_machine.transition_state('ctf_rush', {})
        elif state == 'def':
            self.state_machine.transition_state('ctf_def', {})
        elif state == 'mid':
            self.state_machine.transition_state('ctf_mid', {})
        elif state == 'flagbearer':
            self.state_machine.transition_state('ctf_flagbearer', {})
        elif state == 'flagsaver':
            self.state_machine.transition_state('ctf_flagsaver', {})
        elif state == 'flagchaser':
            self.state_machine.transition_state('ctf_flagchaser', {})
        elif state == 'flagrush':
            self.state_machine.transition_state('ctf_flagrush', {})

        # # If we have no enemies, just capture!
        # if self.state_machine.game_state.no_enemies_in_game:
        #     # Move to rush_capture
        #     self.state_machine.transition_state('ctf_rush_grab_flag', {})

        