
from model.states.state import State
from butils.utils import *

class ctf_main(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.player_tracking = 0
        self.patrol_coords = []

    def enter(self, msg:dict):
        self.starting_coord = self.state_machine.game_state.player.coord
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

    def engage(self):
        ### Engage
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)

        if calculate_distance(self.starting_coord, self.state_machine.game_state.player.coord) > 1000 or self.patrol_coords == []:
            self.starting_coord = self.state_machine.game_state.player.coord
            # Get new patrol coordinates
            self.patrol_coords = [self.state_machine.game_state.map.get_random_coord_nearby(self.starting_coord, dist=500) for _ in range(4)]

        self.state_machine.patrol(self.patrol_coords)

        enemy_health = self.state_machine.game_state.players[self.player_tracking].health

        if self.state_machine.profile.overall_skill <= 4:
            self.state_machine.change_weapon('grav')
            self.state_machine.fire_weapon(object_id=self.player_tracking)
        elif self.state_machine.profile.overall_skill <= 6:
            if enemy_health <= 50 and calculate_distance(self.state_machine.target, self.state_machine.game_state.player.coord) < 900:
                self.state_machine.change_weapon('blitz')
                self.state_machine.fire_weapon(object_id=self.player_tracking)
            else:
                self.state_machine.change_weapon('grav')
                self.state_machine.fire_weapon(object_id=self.player_tracking)
        else: # > 7
            if enemy_health <= 90 and calculate_distance(self.state_machine.target, self.state_machine.game_state.player.coord) < 1300:
                self.state_machine.change_weapon('blitz')
            elif calculate_distance(self.state_machine.target, self.state_machine.game_state.player.coord) < 400:
                self.state_machine.change_weapon('blitz')
            else:
                self.state_machine.cycle_weapons(['grav', 'flux'])

            self.state_machine.fire_weapon(object_id=self.player_tracking)