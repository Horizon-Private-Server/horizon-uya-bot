import os
import json
import numpy as np

from model.player_state import PlayerState

class GameState:
    def __init__(self, gameinfo:dict, player:PlayerState):
        self.player = player

        self.players = {} # player id -> PlayerState

        self.state = 'staging'

        self.game_name = gameinfo['game_name']
        # ['Flux', 'N60', 'Blitz', 'Rockets', 'Gravity Bomb', 'Mines', "Morph O' Ray", 'Lava Gun']
        self.allowed_weapons = gameinfo['weapons']
        # {'baseDefenses': True, 'spawn_charge_boots': False, 'spawn_weapons': False, 'player_names': True, 'vehicles': True}
        self.advanced_rules = gameinfo['advanced_rules']
        # ['Bakisi_Isle', 'Hoven_Gorge', 'Outpost_x12', 'Korgon_Outpost', 'Metropolis', 'Blackwater_City', 'Command_Center', 'Aquatos_Sewers', 'Blackwater_Dox', 'Marcadia_Palace']
        self.map = gameinfo['map']
        # ['Siege', 'CTF', 'Deathmatch']
        self.game_mode = gameinfo['game_mode']

        # Point grid
        self.grid = self._read_map()


    def time_update(self, src_player: int, time: int):
        if src_player not in self.players.keys():
            return
        self.players[src_player].time = time

    def movement_update(self, src_player:int, movement_data:dict):
        if src_player not in self.players.keys():
            return
        self.players[src_player].coord = movement_data['coord']
        self.players[src_player].movement_packet_num = movement_data['packet_num']

    def tnw_playerdata_update(self, src_player:int, tnw_playerdata: dict):
        self.players[src_player] = PlayerState(src_player, tnw_playerdata['account_id_1'], tnw_playerdata['team'])

    def __str__(self):
        result = f'''
=============================================
                GameState
---------------------------------------------
Map:{self.map} GameMode:{self.game_mode}
State:{self.state} PlayerCount:{len(self.players)+1}
---------------------------------------------
{self.player}
---------------------------------------------
'''
        for player in self.players.values():
            result += str(player) + '\n'
        result += '============================================='
        return result

    def _read_map(self):
        with open(os.path.join('maps', f'{self.map}.json'), 'r') as f:
            return np.array(json.loads(f.read()))
