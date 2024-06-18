
from model.states.state import State
from butils.utils import *

class training_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)

    def enter(self, msg:dict):
        self.starting_coord = self.state_machine.game_state.player.coord
        self.state_machine.target = self.state_machine.game_state.players[0].coord
        self.patrol_coords = []

    def update(self):
        self.state_machine.target = self.state_machine.game_state.players[0].coord

        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        # Target too far!
        if target_distance > 1800:
            self.state_machine.transition_state('training_target_toofar', {})
            return

        if self.state_machine.bot_mode == 'training idle':
            self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)
            return
        
        elif self.state_machine.bot_mode == 'training passive':
            if calculate_distance(self.starting_coord, self.state_machine.game_state.player.coord) > 1000 or self.patrol_coords == []:

                self.starting_coord = self.state_machine.game_state.player.coord
                # Get new patrol coordinates
                self.patrol_coords = []
                for _ in range(4):
                    self.patrol_coords.append(self.state_machine.game_state.map.get_random_coord_nearby(self.starting_coord, dist=500))

            #print(self.patrol_coords)
            self.state_machine.patrol(self.patrol_coords)