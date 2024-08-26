
from model.states.state import State
from butils.utils import *

class god_initial(State):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.player_tracking = 0
        self.patrol_coords = []
        state_machine.cycle_timing = 5
        state_machine.weapon_switch_fire_cooldown = .1
        state_machine.profile.grav_hit_percent = 1
        state_machine.game_state.player.arsenal.weapons['flux']['hit_rate'] = 1
        state_machine.game_state.player.arsenal.weapons['grav']['hit_rate'] = 1
        state_machine.game_state.player.arsenal.weapons['flux']['cooldown'] = .1
        state_machine.game_state.player.arsenal.weapons['grav']['cooldown'] = .1
        state_machine.game_state.player._default_health = 1000

    def enter(self, msg:dict):
        self.starting_coord = self.state_machine.game_state.player.coord
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

    def update(self):
        self.player_tracking = self.state_machine.game_state.get_closest_enemy_player()
        self.state_machine.target = self.state_machine.game_state.players[self.player_tracking].coord

        self.state_machine.update_joystick_input_and_angle(self.state_machine.game_state.player.coord, self.state_machine.game_state.player.coord)

        target_distance = calculate_distance(self.state_machine.game_state.player.coord, self.state_machine.target)
        # Target too far!
        if target_distance > 2000:
            self.state_machine.transition_state('god_target_toofar', {})
            return

        if calculate_distance(self.starting_coord, self.state_machine.game_state.player.coord) > 1000 or self.patrol_coords == []:
            self.starting_coord = self.state_machine.game_state.player.coord
            # Get new patrol coordinates
            self.patrol_coords = [self.state_machine.game_state.map.get_random_coord_nearby(self.starting_coord, dist=500) for _ in range(4)]

        ### Lets go crouch 'em
        if self.state_machine.game_state.nothing_to_do() and self.state_machine.profile.overall_skill >= 8:
            self.state_machine.transition_state('god_crouch_body', {})
            return

        ### Engage
        self.state_machine.patrol(self.patrol_coords)

        enemy_health = self.state_machine.game_state.players[self.player_tracking].health

        self.state_machine.cycle_weapons(['grav', 'flux'])
        self.state_machine.fire_weapon(object_id=self.player_tracking)

        