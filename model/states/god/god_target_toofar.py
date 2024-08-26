from model.states.state import State
from butils.utils import *

class god_target_toofar(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self._min_dist = 1400

    def enter(self, msg:dict):
        self.state_machine.target = self.state_machine.game_state.players[0].coord
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.change_weapon('grav')

    def update(self):
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

        self.state_machine.fire_weapon(object_id=self.player_tracking)

        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        if target_distance > self._min_dist:
            new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.state_machine.target, chargeboot=True)
            self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, new_coord)
            self.state_machine.game_state.player.set_coord(new_coord)
        else:
            self.state_machine.transition_state('god_initial', {})

