
from model.states.state import State
from butils.utils import *

class metric_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        #self.starting_coord = [27205, 54135, 7418] # Marc by flag drop
        self.starting_coord = [34519, 54146, 7324] # Marc next to red flag



    def update(self):
        self.state_machine.game_state.player.coord = self.starting_coord
        self.state_machine.target = self.state_machine.game_state.players[0].coord
        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)
