
from model.states.state import State
from butils.utils import *

class dm_crouch_body(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)





    def enter(self, msg:dict):
        self.starting_coord = self.state_machine.game_state.player.coord
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

    def update(self):
        if not self.state_machine.game_state.nothing_to_do():
            self.state_machine.transition_state('dm_initial', {})
            return
        
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

        # Run to the body
        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        if target_distance > 100:
            new_coord = self.state_machine.game_state.map.path(self.state_machine.game_state.player.coord, self.state_machine.target, chargeboot=True)
            self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, new_coord)
            self.state_machine.game_state.player.set_coord(new_coord)
            return

        # Crouch
        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)
        if self.state_machine.game_state.player.prev_animation == 'aim-crouch1':
            self.state_machine.game_state.player.animation = 'aim-crouch2'
        else:
            self.state_machine.game_state.player.animation = 'aim-crouch1'

