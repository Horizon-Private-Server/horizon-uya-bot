

class PlayerState:
    def __init__(self, player_id:int=None, account_id:int=None, team:str=None, username:str=None, skin:str=None, clan_tag:str=None, rank:int=0):
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

        self.coord = [0,0,0]
        self.cam_x = 0
        self.movement_packet_num = 0
        self.time = 0

        self.weapon = None
        self.is_dead = False
        self.animation = None
        self._default_health = 100
        self.reset_health()
        self.respawn_time = None

        self.left_joystick_x = None
        self.left_joystick_y = None

        self.flag = None

    def reset_health(self):
        self.health = self._default_health

    def gen_packet_num(self):
        self.movement_packet_num += 1
        if self.movement_packet_num == 256:
            self.movement_packet_num = 0
            return 0
        return self.movement_packet_num - 1

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
                f"coord:{self.coord} movement_packet_num:{self.movement_packet_num} time:{self.time} flag:{self.flag}"
