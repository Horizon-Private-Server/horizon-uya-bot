from model.states.state import State
from butils.utils import *

class ctf_rush_grab_flag(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        if self.state_machine.game_state.player.team == 'blue':
            self.dest_point = self.state_machine.game_state.object_manager.red_flag.initial_location
        else:
            self.dest_point = self.state_machine.game_state.object_manager.blue_flag.initial_location
        self.state_machine.target = self.dest_point

    def update(self):
        if self.state_machine.game_state.player_has_flag():
            # Return to capture
            self.state_machine.transition_state('ctf_rush_return_flag', {})

        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.state_machine.target, chargeboot=True)
        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, new_coord)
        self.state_machine.game_state.player.set_coord(new_coord)

