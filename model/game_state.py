import logging
logger = logging.getLogger('thug.game_state')
logger.setLevel(logging.INFO)

import os
import json
import numpy as np
from collections import defaultdict
from datetime import datetime
import pandas as pd
import asyncio

from maps.map import Map

from model.player_state import PlayerState
from model.object_manager import ObjectManager

from constants.constants import get_flag_location, DEATHMATCH_MAP

from butils.utils import *
from medius.dme_packets import *

class GameState:
    def __init__(self, model, gameinfo:dict, player:PlayerState):
        self.model = model
        self.player = player

        self.players = {} # player id -> PlayerState

        self.state = 'staging'

        self.game_name = gameinfo['game_name']
        # ['flux', 'n60', 'blitz', 'rocket', 'grav', 'mine', 'morph', 'lava']
        self.weapons = list(set(gameinfo['weapons']).intersection({'flux', 'grav', 'blitz'}))

        # {'baseDefenses': True, 'spawn_charge_boots': False, 'spawn_weapons': False, 'player_names': True, 'vehicles': True}
        self.advanced_rules = gameinfo['advanced_rules']
        # ['Bakisi_Isle', 'Hoven_Gorge', 'Outpost_x12', 'Korgon_Outpost', 'Metropolis', 'Blackwater_City', 'Command_Center', 'Aquatos_Sewers', 'Blackwater_Dox', 'Marcadia_Palace']
        self.map_name = gameinfo['map']
        # ['Siege', 'CTF', 'Deathmatch']
        self.game_mode = gameinfo['game_mode']

        self.game_info = gameinfo

        self.nodes = True

        self.start_time = datetime.now()

        # Point grid
        self.map = Map(self.map_name)

        self.red_caps = 0
        self.blue_caps = 0

        self.object_manager = ObjectManager(self.model, self, self.map_name, self.game_mode)

        self.no_enemies_in_game = True

    def get_closest_enemy_player(self):
        player_chosen = None
        player_dist = 999999

        for player_idx, player in self.players.items():
            if calculate_distance(player.coord, self.player.coord) < player_dist and player.team != self.player.team and not player.is_dead:
                player_chosen = player_idx
                player_dist = calculate_distance(player.coord, self.player.coord)

        if player_chosen == None: # Get closest dead player
            for player_idx, player in self.players.items():
                if calculate_distance(player.coord, self.player.coord) < player_dist and player.team != self.player.team:
                    player_chosen = player_idx
                    player_dist = calculate_distance(player.coord, self.player.coord)

        if player_chosen == None:
            return 0

        return player_chosen


    def nothing_to_do(self):
        # If all enemies players are dead and game mode = DM, lets go crouch em
        if self.game_mode == 'Deathmatch':
            closest_enemy = self.get_closest_enemy_player()
            if self.players[closest_enemy].team == self.player.team or self.players[closest_enemy].is_dead:
                return True
        
        return False

    def start(self):
        self.player.set_coord(self.map.get_respawn_location(self.player.team, self.game_mode))

    def game_started(self):
        # Actual game has started
        self.start_time = datetime.now()

    def timed_out(self):
        if self.game_info['game_length'] != None:
            if ((datetime.now() - self.start_time).total_seconds() / 60) > self.game_info['game_length']:
                return True
        return False

    def player_left(self, src_player:int):
        if src_player not in self.players.keys():
            return
        del self.players[src_player]

    def player_killed(self, killer_id: int, killed_id: int):
        if killer_id == self.player.player_id:
            self.player.total_kills += 1
        else:
            self.players[killer_id].total_kills += 1
        
        if killed_id != self.player.player_id:
            self.players[killed_id].is_dead = True

        if self.game_mode == 'Deathmatch' and self.game_info['frag'] != None:
            # Add up total score per team. See if it reaches frag
            team_scores = defaultdict(int)
            team_scores[self.player.team] += self.player.total_kills
            for player in self.players.values():
                team_scores[player.team] += player.total_kills
            
            for total_score in team_scores.values():
                if total_score >= self.game_info['frag']:
                    logger.info(f"Got more kills than frag limit ({self.game_info['frag']})!")
                    self.model.loop.create_task(self.model.kill(delay=5))
                    return


    def time_update(self, src_player: int, time: int):
        if src_player not in self.players.keys():
            return
        self.players[src_player].time = time

    def movement_update(self, src_player:int, movement_data:dict):
        if src_player not in self.players.keys():
            return
        self.players[src_player].set_coord(movement_data['coord'])
        self.players[src_player].set_area(self.map.get_area(movement_data['coord']))
        self.players[src_player].cam_x = movement_data['cam3_x']
        self.players[src_player].movement_packet_num = movement_data['packet_num']

        if self.players[src_player].flag == 'red_flag':
            self.red_flag_loc = movement_data['coord']
        elif self.players[src_player].flag == 'blue_flag':
            self.blue_flag_loc = movement_data['coord']

    def tnw_playerdata_update(self, src_player:int, tnw_playerdata: dict):
        # No longer needed since we update on gamesetting
        '''
        if src_player in self.players.keys():
            self.players[src_player].player_id = src_player
            self.players[src_player].account_id = tnw_playerdata['account_id_1']
            self.players[src_player].team = tnw_playerdata['team']
        else:
            self.players[src_player] = PlayerState(player_id=src_player, account_id=tnw_playerdata['account_id_1'], team=tnw_playerdata['team'])
        '''
        return


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


            if username == self.player.username:
                self.player.player_id = player_idx
                self.player.team = team
            elif username == '' or username == None:
                continue
            else:
                # Real player
                self.players[player_idx] = PlayerState(player_id=player_idx, account_id=0, team=team, username=username, skin=skin, clan_tag=clan_tag, rank=1)

        self.nodes = tnw_gamesetting['nodes']

        self.no_enemies_in_game = True
        for player in self.players.values():
            if player.team != self.player.team:
                self.no_enemies_in_game = False



    def _read_map(self):
        with open(os.path.join('maps', f'{self.map}.json'), 'r') as f:
            return np.array(json.loads(f.read()))


###################################################
# CTF Methods
###################################################

    def player_has_flag(self):
        return self.object_manager.red_flag.holder == self.player.player_id or self.object_manager.blue_flag.holder == self.player.player_id

    async def player_drop_flag(self):
        await asyncio.sleep(0.5)
        if self.player.team == 'red':
            flag = self.object_manager.blue_flag
        elif self.player.team == 'blue':
            flag = self.object_manager.red_flag

        flag.dropped(self.player.coord)
        coord = self.map.transform_global_to_local(self.player.coord)
        data = {'local_x': coord[0], 'local_y': coord[1], 'local_z': coord[2]}
        self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.player.player_id}_flag_drop', object_type=flag.id,timestamp=self.player.time,data=data)])


    def home_flag_dropped(self):
        if self.player.team == 'red' and self.object_manager.red_flag.is_dropped():
            return True
        elif self.player.team == 'blue' and self.object_manager.blue_flag.is_dropped():
            return True
        return False
    
    def enemy_flag_dropped(self):
        if self.player.team == 'red' and self.object_manager.blue_flag.is_dropped():
            return True
        elif self.player.team == 'blue' and self.object_manager.red_flag.is_dropped():
            return True
        return False

    def get_home_flag_location(self):
        if self.player.team == 'red':
            return self.object_manager.red_flag.location
        return self.object_manager.blue_flag.location
    
    def get_enemy_flag_location(self):
        if self.player.team == 'red':
            return self.object_manager.blue_flag.location
        return self.object_manager.red_flag.location

    def flag_no_enemies_nearby(self, location):
        flag_enemy_dist = 2000

        for player in self.players.values():
            player_distance = calculate_distance(location, player.coord)
            if player.team != self.player.team and player_distance < flag_enemy_dist and not player.is_dead:
                return False
            
        return True

    def home_flag_reachable(self):
        home_flag_loc = self.get_home_flag_location()
        return self.map.point_reachable(home_flag_loc)

    def enemy_flag_reachable(self):
        enemy_flag_loc = self.get_enemy_flag_location()
        return self.map.point_reachable(enemy_flag_loc)

    def enemy_flag_at_base(self):
        if self.player.team == 'red' and self.object_manager.blue_flag.is_at_base():
            return True
        elif self.player.team == 'blue' and self.object_manager.red_flag.is_at_base():
            return True
        return False

    def ctf_get_objective(self):
        '''
        Return if we are going to rush/def/mid
        '''

        # Return if we should be currently engaged in a fight with someone
        fight_distance = 1200

        # Check if we have the flag. If we do, then 
        if self.player_has_flag():
            return 'flagbearer'
        
        # If our flag is dropped, there are no enemies nearby, and it is reachable, let's go save it!
        if self.home_flag_dropped() and self.flag_no_enemies_nearby(self.get_home_flag_location()) and self.home_flag_reachable():
            return 'flagsaver'
        
        # TODO: If they have our flag, let's chase them.

        # TODO: If one of our guys has the flag, let's go defend them 

        # If the enemy flag is dropped and is reachable with no enemies, go grab the flag 
        if self.enemy_flag_dropped() and self.flag_no_enemies_nearby(self.get_enemy_flag_location()) and self.enemy_flag_reachable():
            return 'flagchaser'

        for player in self.players.values():
            player_distance = calculate_distance(self.player.coord, player.coord)
            if player.team != self.player.team and player_distance < fight_distance and not player.is_dead:
                return 'engage'

        home_flag = 'base'
        enemy_flag = 'base'
        num_def = 0
        num_mid = 0
        num_rush = 0
        num_enemy_def = 0
        num_enemy_mid = 0
        num_enemy_rush = 0

        for player in self.players.values():
            if player.is_dead:
                continue
            if player.team == self.player.team and self.player.team == 'red':
                if player.area == 'red':
                    num_def += 1
                elif player.area == 'mid':
                    num_mid += 1
                elif player.area == 'blue':
                    num_rush += 1
            elif player.team == self.player.team and self.player.team == 'blue':
                if player.area == 'blue':
                    num_def += 1
                elif player.area == 'mid':
                    num_mid += 1
                elif player.area == 'red':
                    num_rush += 1
            elif player.team != self.player.team and self.player.team == 'red':
                if player.area == 'red':
                    num_enemy_rush += 1
                elif player.area == 'mid':
                    num_enemy_mid += 1
                elif player.area == 'blue':
                    num_enemy_def += 1
            elif player.team != self.player.team and self.player.team == 'blue':
                if player.area == 'red':
                    num_enemy_def += 1
                elif player.area == 'mid':
                    num_enemy_mid += 1
                elif player.area == 'blue':
                    num_enemy_rush += 1

        state = 'def'
        if False:
            pass
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def > 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid > 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush > 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def > 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid > 0 and num_enemy_rush == 0:
            state = 'mid'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush > 0:
            state = 'def'
        elif home_flag == 'base'  and enemy_flag == 'base' and num_def == 0 and num_mid == 0 and num_rush == 0 and num_enemy_def == 0 and num_enemy_mid == 0 and num_enemy_rush == 0:
            state = 'rush'
        
        # logger.info(f"num_def:{num_def} num_mid:{num_mid} num_rush:{num_rush} | num_enemy_def:{num_enemy_def} num_enemy_mid:{num_enemy_mid} num_enemy_rush:{num_enemy_rush}")
        # logger.info(f"STATE: {state}")
        #if not self.enemy_flag_at_base() and state == 'rush':
            
        return state


    def __str__(self):
        result = f'''
=============================================
                GameState
---------------------------------------------
{self.map} {self.game_mode} TimeLim:{self.game_info['game_length']}
Frag:{self.game_info['frag']} CapLim:{self.game_info['cap_limit']}
State:{self.state} PlayerCount:{len(self.players)+1}
Caps- Blue:{self.blue_caps} Red:{self.red_caps}
---------------------------------------------
{self.model.bot}
---------------------------------------------
{self.player}
---------------------------------------------
'''
        for player in self.players.values():
            result += str(player) + '\n'
        result += '====================\n'
        result += 'Object Manager\n'
        result += str(self.object_manager) + '\n'
        result += '============================================='
        return result


