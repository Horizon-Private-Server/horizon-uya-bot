
from model.states.state import State
from model.states.ctf.ctf_main import ctf_main
from butils.utils import *

class ctf_flagbearer(ctf_main):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        super().enter(msg)
        if self.state_machine.game_state.player.team == 'blue':
            self.dest_point = self.state_machine.game_state.object_manager.blue_flag.initial_location
        else:
            self.dest_point = self.state_machine.game_state.object_manager.red_flag.initial_location
        self.state_machine.target = self.dest_point

        # Set hypershot
        self.state_machine.set_initial_weapon()

    def update(self):
        # Get whether to rush/def/mid 
        state = self.state_machine.game_state.ctf_get_objective()
        if state != 'flagbearer':
            self.state_machine.transition_state('ctf_initial', {})
            return

        # Move toward start coord
        new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.dest_point, chargeboot=True)
        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, new_coord)
        self.state_machine.game_state.player.set_coord(new_coord)
