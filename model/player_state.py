import logging
logger = logging.getLogger('thug.player_state')
logger.setLevel(logging.INFO)

from model.arsenal import Arsenal
from datetime import datetime

VALID_HP ={
    100,93,86,80,73,66,60,53,46,40,33,26,20,13,6,0
}

def get_closest_hp(input_number):
    return min(VALID_HP, key=lambda x: abs(x - input_number))

class PlayerState:
    def __init__(self, player_id:int=None, account_id:int=None, team:str='blue', username:str=None, skin:str=None, clan_tag:str=None, rank:int=0):
        self.player_id = player_id
        self.account_id = account_id
        self.team = team
        self.username = username
        self.skin = skin
        self.clan_tag = clan_tag
        rank_map = {
            0: '',
            1: '00C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF43',
            2: '00C0A84400C0A84400C0A84400C0A84400808443008084430080844300808443',
            3: '00C0A84400C0A84400C0A84400C0A84400000000000000000000000000000000',
            4: 'C8C8D444C8C8D444C8C8D444C8C8D44400808943008089430080894300808943'
        }
        self.rank = rank_map[rank]

        self.coord_timestamp = datetime.now()
        self.coord = [0,0,0]
        self.cam_x = 0
        self.movement_packet_num = 0
        self.time = 0

        self.weapon = None
        self.is_dead = False
        self.animation = None
        self.prev_animation = None
        self._default_health = 100
        self.health = self._default_health
        self.reset_health()
        self.respawn_time = None

        self.stunned = False

        self.left_joystick_x = None
        self.left_joystick_y = None

        self.flag = None

        self.total_kills = 0

        self.area = 'red'

        self.arsenal = Arsenal()

    def take_damage(self, damage):
        self.health -= damage
        self.health = max(self.health,0)
        self.health = get_closest_hp(self.health)

    def reset_health(self):
        self.health = self._default_health

    def gen_packet_num(self):
        self.movement_packet_num += 1
        if self.movement_packet_num == 256:
            self.movement_packet_num = 0
            return 0
        return self.movement_packet_num - 1
    
    def set_coord(self, new_coord):
        self.coord_timestamp = datetime.now()

        if self.stunned or self.is_dead:
            return

        self.coord = new_coord

    def set_area(self, area: str):
        self.area = area

    def respawn(self):
        self.is_dead = False
        self.stunned = False
        self.weapon = None
        self.reset_health()
        self.arsenal.reset_upgrades()

    def change_teams(self, game_mode):
        team_change_map = {
            'blue': 'red',
            'red': 'green',
            'green': 'orange',
            'orange': 'yellow',
            'yellow': 'purple',
            'purple': 'aqua',
            'aqua': 'pink',
            'pink': 'blue'
        }
        ctf_siege_map = {
            'red': 'blue',
            'blue': 'red'
        }

        if game_mode == 'Deathmatch':
            self.team = team_change_map[self.team]
        else:
            self.team = ctf_siege_map[self.team]
        return self.team

    def __str__(self):
        return f"PlayerState; username: {self.username} player_id:{self.player_id} account_id:{self.account_id} team:{self.team} health:{self.health} is_dead:{self.is_dead}  weapon:{self.weapon} " + \
                f"coord:{self.coord} movement_packet_num:{self.movement_packet_num} time:{self.time} flag:{self.flag} area:{self.area} arsenal: {self.arsenal} total_kills:{self.total_kills}"
