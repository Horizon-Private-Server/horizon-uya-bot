from model.states.state import State
from butils.utils import *

class training_target_toofar(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self._min_dist = 1400

    def enter(self, msg:dict):
        self.state_machine.target = self.state_machine.game_state.players[0].coord

    def update(self):
        self.state_machine.target = self.state_machine.game_state.players[0].coord

        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        if target_distance > self._min_dist:
            new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.state_machine.target)
            self.state_machine.update_animation_and_angle(self.state_machine.game_state.player.coord, new_coord)
            self.state_machine.game_state.player.set_coord(new_coord)
            return
        else:
            self.state_machine.transition_state('training_initial', {})
            return