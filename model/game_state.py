import os
import json
import numpy as np

from maps.map import Map

from model.player_state import PlayerState

from constants.constants import get_flag_location

class GameState:
    def __init__(self, gameinfo:dict, player:PlayerState):
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

        self.red_flag_loc = get_flag_location(map=self.map_name, team='red')
        self.blue_flag_loc = get_flag_location(map=self.map_name, team='blue')

        # Point grid
        self.map = Map(self.map_name)

    def start(self):
        self.map.read_map()
        self.player.coord = self.map.get_respawn_location(self.player.team, self.game_mode)


    def clear_flag(self, flag):
        if self.player.flag == flag:
            self.player.flag = None
            return

        for player_id in self.players.keys():
            if self.players[player_id].flag == flag:
                self.players[player_id].flag = None

        if flag == 'red_flag':
            self.red_flag_loc = get_flag_location(map=self.map_name, team='red')
        elif flag == 'blue_flag':
            self.blue_flag_loc = get_flag_location(map=self.map_name, team='blue')

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

        if self.players[src_player].flag == 'red_flag':
            self.red_flag_loc = movement_data['coord']
        elif self.players[src_player].flag == 'blue_flag':
            self.blue_flag_loc = movement_data['coord']

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
Red Flag:{self.red_flag_loc} Blue Flag:{self.blue_flag_loc}
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
