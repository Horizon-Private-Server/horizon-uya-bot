

from model.states.state import State
from butils.utils import *

class follow_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.player_tracking = 0

    def enter(self, msg:dict):
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()

    def update(self):
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)

        if calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target) > 200:
            new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.state_machine.target, chargeboot=True)
            self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, new_coord)
            self.state_machine.game_state.player.set_coord(new_coord)