from datetime import datetime, timedelta
from collections import deque

from live.player_state import PlayerState


class GameState:
    def __init__(self, world_id, world_timeout):
        self.world_id = world_id
        self.world_timeout = world_timeout
        self.world_latest_update = datetime.now()


        self.players = {} # player id -> PlayerState
        self.events = deque(maxlen=100)

    def tnw_gamesetting_update(self, src_player:int, tnw_gamesetting: dict):
        '''
2024-05-19 21:38:20,749 blarg | INFO | 0 -> -1 | tcp_0004_tnw; tnw_type:tNW_GameSetting data:{'unk1': '00010000040000000000FF41C5EFA50000000000', 'p0_username': 'FourBolt', 'p1_username': 'Ceejee', 'p2_username': 'Jumper', 'p3_username': 'raZorX', 'p4_username': 'sombra', 'p5_username': 'Fatallica', 'p6_username': 'cameron', 'p7_username': 'Nelo', 'p0_clan_tag': '', 'p1_clan_tag': '\x0cCPU', 'p2_clan_tag': '\x0cCPU', 'p3_clan_tag': '\x0cCPU', 'p4_clan_tag': '\x0cCPU', 'p5_clan_tag': '\x0cCPU', 'p6_clan_tag': '\x0cCPU', 'p7_clan_tag': '\x0cCPU', 'p0_skin': 'skrunch', 'p1_skin': 'ninja', 'p2_skin': 'buginoid', 'p3_skin': 'buginoid', 'p4_skin': 'gladiola', 'p5_skin': 'trooper', 'p6_skin': 'beach bunny', 'p7_skin': 'trooper', 'p0_team': 'blue', 'p1_team': 'red', 'p2_team': 'green', 'p3_team': 'orange', 'p4_team': 'yellow', 'p5_team': 'purple', 'p6_team': 'aqua', 'p7_team': 'pink', 'unk2': '000001000200030004000500060007000700060006000600060006000600060008000000FFFFFFFFFE3DA80031000000020000000000000000000000000000', 'nodes': False, 'unk3': '000101000001001903150101010000010200000070030000710300007303000074030000760300007503000072030000', 'p0_bolt_modifier': 'FA27DF44', 'p1_bolt_modifier': 'C8C8D444', 'p2_bolt_modifier': 'C8C8D444', 'p3_bolt_modifier': 'C8C8D444', 'p4_bolt_modifier': 'C8C8D444', 'p5_bolt_modifier': 'C8C8D444', 'p6_bolt_modifier': 'C8C8D444', 'p7_bolt_modifier': 'C8C8D444', 'p0_bolt_skill': '0000AA43', 'p1_bolt_skill': '00808943', 'p2_bolt_skill': '00808943', 'p3_bolt_skill': '00808943', 'p4_bolt_skill': '00808943', 'p5_bolt_skill': '00808943', 'p6_bolt_skill': '00808943', 'p7_bolt_skill': '00808943'}

        '''
        self.players = {}
        for player_idx in range(8):
            username = tnw_gamesetting[f'p{player_idx}_username']
            team = tnw_gamesetting[f'p{player_idx}_team']
            clan_tag = tnw_gamesetting[f'p{player_idx}_clan_tag']
            skin = tnw_gamesetting[f'p{player_idx}_skin']

            if username == '' or username == None:
                continue
            else:
                # Real player
                self.players[player_idx] = PlayerState(player_id=player_idx, account_id=-1, team=team, username=username, skin=skin, clan_tag=clan_tag, rank=1)

    def reset_arsenal(self, src_player:int):
        if src_player in self.players.keys():
            self.players[src_player].reset_arsenal()

    def set_weapon_upgrades(self, src_player:int, upgrades:dict):
        if src_player in self.players.keys():
            self.players[src_player].set_upgrades(upgrades)

    def movement_update(self, src_player:int, movement_data:dict):
        if src_player not in self.players.keys():
            self.players[src_player] = PlayerState(player_id=src_player)
        self.players[src_player].coord = movement_data['coord']
        self.players[src_player].cam_x = movement_data['cam3_x']

    def health_update(self, src_player:int, health: int):
        self.players[src_player].health = health

    def timed_out(self):
        return (datetime.now() - self.world_latest_update).total_seconds() > self.world_timeout

    def player_killed(self, killer_id:int, killed_id:int, weapon:str):
        if weapon == 'flux':
            pass
        elif weapon == 'grav':
            pass
        elif weapon == 'blitz':
            pass
        if killer_id in self.players.keys():
            self.players[killer_id].total_kills += 1
        if killer_id == 255:
            self.players[killed_id].total_suicides += 1
        if killed_id in self.players.keys():
            self.players[killed_id].total_deaths += 1

    def to_json(self):
        return {
            'world_id': self.world_id,
            'world_latest_update': str(self.world_latest_update),
            'players': [player.to_json() for player in self.players.values()],
            'events': list(self.events),
            'map': 'UNKNOWN',
            'name': 'UNKNOWN',
            'game_mode': 'UNKNOWN',
        }
    
    def update(self):
        self.world_latest_update = datetime.now()


    def flag_capture(self, src_player: int):
        if src_player in self.players.keys():
            self.players[src_player].total_flags += 1