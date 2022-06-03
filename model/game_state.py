import os
import json
import numpy as np

from maps.map import Map

from model.player_state import PlayerState

class GameState:
    def __init__(self, gameinfo:dict, player:PlayerState, config:dict):
        self.player = player

        self.players = {} # player id -> PlayerState

        self.state = 'staging'

        self.game_name = gameinfo['game_name']
        # ['flux', 'n60', 'blitz', 'rocket', 'grav', 'mine', 'morph', 'lava']
        self.weapons = list(set(gameinfo['weapons']).intersection({'flux', 'rocket', 'grav', 'n60'}))

        # {'baseDefenses': True, 'spawn_charge_boots': False, 'spawn_weapons': False, 'player_names': True, 'vehicles': True}
        self.advanced_rules = gameinfo['advanced_rules']
        # ['Bakisi_Isle', 'Hoven_Gorge', 'Outpost_x12', 'Korgon_Outpost', 'Metropolis', 'Blackwater_City', 'Command_Center', 'Aquatos_Sewers', 'Blackwater_Dox', 'Marcadia_Palace']
        self.map_name = gameinfo['map']
        # ['Siege', 'CTF', 'Deathmatch']
        self.game_mode = gameinfo['game_mode']

        self.game_info = gameinfo

        self.nodes = True

        # Point grid
        self.map = Map(self.map_name)

    def player_left(self, src_player:int):
        if src_player not in self.players.keys():
            return
        del self.players[src_player]

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
        if src_player in self.players.keys():
            self.players[src_player].player_id = src_player
            self.players[src_player].account_id = tnw_playerdata['account_id_1']
            self.players[src_player].team = tnw_playerdata['team']
        else:
            self.players[src_player] = PlayerState(player_id=src_player, account_id=tnw_playerdata['account_id_1'], team=tnw_playerdata['team'])

    def tnw_gamesetting_update(self, src_player:int, tnw_gamesetting: dict):
        for player_idx in range(8):
            if player_idx == self.player.player_id:
                continue

            username = tnw_gamesetting[f'p{player_idx}_username']
            if username != '':
                # Update username
                if player_idx in self.players.keys():
                    self.players[player_idx].username = username
                else:
                    self.players[player_idx] = PlayerState(player_id=player_idx, username = username)
        self.nodes = tnw_gamesetting['nodes']

    def __str__(self):
        result = f'''
=============================================
                GameState
---------------------------------------------
Map:{self.map} GameMode:{self.game_mode} Nodes:{self.nodes}
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
