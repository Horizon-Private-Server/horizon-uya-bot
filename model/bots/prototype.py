import asyncio
import random
from scipy.spatial import distance
from datetime import datetime
from collections import defaultdict

from constants.constants import ANIMATION_MAP, MAIN_BOT_LOOP_TIMER
from medius.dme_packets import *
from butils.utils import *

from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer

from model.arsenal import Arsenal

import logging
logger = logging.getLogger('thug.model.prototype')
logger.setLevel(logging.INFO)

class prototype:
    def __init__(self, model, game_state):
        self._model = model
        self.game_state = game_state

        # self.game_state.player.coord = self.game_state.map.get_respawn_location(self.game_state.player.team, self.game_state.game_mode)
        self.game_state.player.coord = [0,0,0]
        self.game_state.player.x_angle = 127

        self.tracking = self.game_state.player

        self.follow_player = False

        self.arsenal = Arsenal()

        self.cpu_damage_min_dist = 800

        self.respawn_time = 5

        self.weapon_switch_fire_cooldown = .3
        self.weapon_switch_dt = datetime.now().timestamp()

        self._close_weapon_self_dmg_rate = {
            'grav': .4,
            'blitz': .5,
            'lava': .5
        }

        self._close_weapon_self_dmg_amount = {
            'grav': 20,
            'blitz': 10,
            'lava': 10
        }

        self._misc = defaultdict(int)

    async def main_loop(self):
        while self._model.alive:
            try:
                if self.game_state.players[0].coord == [0,0,0]:
                    pass
                else:

                    self.tracking = self.game_state.players[0]

                    # Randomly pick a valid weapon if no weapon is selected
                    if self.game_state.player.weapon == None:
                        self.change_weapon()

                    # Respawn
                    if self.game_state.player.is_dead and datetime.now().timestamp() > self.game_state.player.respawn_time:
                        self.respawn()

                    # Run objective
                    #self.objective()
                    #self.game_state.player.coord = [28593, 54682, 7413]

                    # Patrol marc flag to flag
                    #self.patrol([34161, 54135, 7413],[27114, 54160, 7413])

                    # Patrol marc 1 base:
                    #self.patrol([28450, 55272, 7413], [28752, 54612, 7413], [27149, 54243, 7421])

                    #new_coord = self.game_state.map.path(self.game_state.player.coord, self._misc['patrol'])
                    self.game_state.player.coord = [28752, 54612, 7413]
                    self.update_animation_and_angle([28752, 54612, 7413], [28752, 54612, 7413], [27149, 54243, 7421])

                    # Fire weapon
                    self.fire_weapon()

                    # Send movement
                    self.send_movement()

                # Sleep for the loop
                await asyncio.sleep(MAIN_BOT_LOOP_TIMER)
            except:
                logger.exception("PROTOTYPE ERROR")
                self._model.alive = False
                break

    def send_movement(self):
        if self.game_state.players[0].coord == [0,0,0]:
            return

        packet_num = self.game_state.player.gen_packet_num()
        data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': self.game_state.player.x_angle, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': self.game_state.player.x_angle, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': self.game_state.player.x_angle, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': self.game_state.player.x_angle, 'buffer': '00', 'coord': self.game_state.player.coord, 'packet_num': packet_num, 'flush_type': 0, 'type': 'movement'}

        if self.game_state.player.animation != None:
            data['flush_type'] = 16
            data['animation'] = self.game_state.player.animation

        if self.game_state.player.left_joystick_x != None:
            data['left_joystick_x'] = self.game_state.player.left_joystick_x
            data['left_joystick_y'] = self.game_state.player.left_joystick_y

        self._model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])


    def patrol(self, coord1, coord2, target):
        
        if 'patrol' not in self._misc.keys():
            self._misc['patrol'] = coord1

        if calculate_distance(self.game_state.player.coord, coord1) < 70:
            self._misc['patrol'] = coord2
        elif calculate_distance(self.game_state.player.coord, coord2) < 70:
            self._misc['patrol'] = coord1
    
        # Red flag marcadia over lip: [34161, 54135, 7413]
        # Blue flag marcadia over lip: [27114, 54160, 7413]
        new_coord = self.game_state.map.path(self.game_state.player.coord, self._misc['patrol'])
        self.update_animation_and_angle(self.game_state.player.coord, new_coord, target)
        self.game_state.player.coord = new_coord


    def objective(self):
        # first determine the state of the flag etc

        # update angle/coord
        if not self.game_state.player.is_dead:
            #if self.game_state.player.movement_packet_num % 4 == 0:

            self.tracking = self._model.get_closest_enemy_player()

            # if we are at 300 distance, we can strafe around instead of walking toward them
            if calculate_distance(self.game_state.player.coord, self.tracking.coord) > 600 or self.follow_player == True:
                new_coord = self.game_state.map.path(self.game_state.player.coord, self.tracking.coord)
                dist_diff = calculate_distance(self.game_state.player.coord, new_coord)
                # logger.info(f"DISTANCE BETWEEN SELECTED AND CURRENT POINT: {dist_diff}")
            else:
                new_coord = self.game_state.map.get_random_coord_connected(self.game_state.player.coord)

            self.game_state.player.animation = self.get_animation(self.game_state.player.coord, new_coord)

            self.game_state.player.coord = new_coord

        # Update camera angle
        # if self.game_state.player.movement_packet_num % 5 == 0:
            self.game_state.player.x_angle = calculate_angle(self.game_state.player.coord, self.tracking.coord)

        # Fire weapon
        #self.fire_weapon()

    def update_animation_and_angle(self, old_coord, new_coord, target_coord):
        # Start with no animation
        self.game_state.player.animation = None

        self.game_state.player.x_angle = calculate_angle(new_coord, target_coord)
        if old_coord == new_coord:
            self.game_state.player.animation = None
            self.game_state.player.left_joystick_x = None
            self.game_state.player.left_joystick_y = None
            return

        if new_coord[2] > old_coord[2]:
            self.game_state.player.animation = 'jump'

        # if random.random() > .5:
        #     self.game_state.player.animation = 'crouch'



        angle = compute_strafe_angle(old_coord, new_coord, target_coord)

        #logger.info(f"{old_coord} | {new_coord} | {target_coord}")

        strafe_direction = get_strafe_direction(old_coord, new_coord, target_coord)
        strafe_angle_joystick = strafe_joystick_input(angle, strafe_direction)

        self.game_state.player.left_joystick_x = strafe_angle_joystick[0]
        self.game_state.player.left_joystick_y = strafe_angle_joystick[1]

        logger.info(f"{self.game_state.player.animation} | {strafe_angle_joystick} | {angle:3.0f} | {strafe_direction}")
        return


        if strafe_magnitude == 'neutral': # Forwards or backwards
            self.game_state.player.animation = forward_direction
        elif strafe_magnitude == 'partial':
            self.game_state.player.animation = f'{forward_direction}-{strafe_direction}'
            #self.game_state.player.animation = f'forward-{strafe_direction}'
        elif strafe_magnitude == 'strafe':
            self.game_state.player.animation = strafe_direction

        logger.info(f"{self.game_state.player.animation:} | {strafe_magnitude} | {forward_direction} | {strafe_direction}")



        # elif new_coord != old_coord:
        #     self.game_state.player.animation = 'forward'


    def respawn(self):
        self.game_state.player.weapon = None
        self.game_state.player.reset_health()
        self._model.dmetcp_queue.put(['B', tcp_020A_player_respawned.tcp_020A_player_respawned(src_player=self.game_state.player.player_id, map=self.game_state.map.map)])
        self.game_state.player.coord = self.game_state.map.get_respawn_location(self.game_state.player.team, self.game_state.game_mode)
        self.game_state.player.is_dead = False

    def fire_weapon(self):
        if self.arsenal.enabled == False or self.game_state.player.is_dead or self.game_state.weapons == [] or self.game_state.player.weapon in [None, 'wrench']:
            return

        if datetime.now().timestamp() - self.weapon_switch_dt < self.weapon_switch_fire_cooldown:
            return

        weapon_fired_bool, hit_bool = self.arsenal.fire_weapon(self.game_state.player.weapon)

        if weapon_fired_bool:
            # Weapon was fired.

            if hit_bool: # player was hit
                #object_id=self.tracking.player_id
                object_id=-1
            else:
                object_id=-1

            # unk2 = hex_to_int_little("00000000") # not needed for flux, needed for gravity
            # unk3 = hex_to_int_little("00000000") # not needed for flux, unknown for gravity
            # unk4 = hex_to_int_little("00000000") # not needed for flux
            # unk5 = hex_to_int_little("0000EF43") # makes flux curve left
            # unk6 = hex_to_int_little("00005C44") # makes flux go backwards
            # unk7 = hex_to_int_little("0000EA42") # last 2 bytes critical, first 2 bytes don't matter


            unk2 = "00000000" # not needed for flux, needed for gravity
            unk3 = "00000000" # not needed for flux, unknown for gravity
            unk4 = "00000000" # not needed for flux
            local_player_coord = self.game_state.map.transform_global_to_local(self.game_state.players[0].coord)

            logger.info(f"TRANSFORMING: {self.game_state.players[0].coord} -> {local_player_coord}")
            local_x = local_player_coord[0] # makes flux curve left
            local_y = local_player_coord[1] # makes flux go backwards
            local_z = local_player_coord[2]+2 # last 2 bytes critical, first 2 bytes don't matter

            # unk2 = hex_to_int_little("FF6EEF43")
            # unk3 = hex_to_int_little("60E95444")
            # unk4 = hex_to_int_little("D99EE942")
            # unk5 = hex_to_int_little("E44BEF43")
            # unk6 = hex_to_int_little("5BBC5C44")
            # unk7 = hex_to_int_little("F5C4EA42")
            # unk2 = 0
            # unk3 = 0
            # unk4 = 0
            # unk5 = 0
            # unk6 = 0
            # unk7 = 0

            self._model.dmetcp_queue.put(['B', packet_020E_shot_fired.packet_020E_shot_fired(network='tcp', map=self.game_state.map.map, weapon=self.game_state.player.weapon,src_player=self.game_state.player.player_id,time=self.game_state.player.time, object_id=object_id, unk1='08', unk2=unk2, unk3=unk3, unk4=unk4, local_x=local_x, local_y=local_y, local_z=local_z)])

            self.posthook_weapon_fired()

    def posthook_weapon_fired(self):
        pass

    def change_weapon(self):
        self.weapon_switch_dt = datetime.now().timestamp()

        if self.game_state.weapons == []:
            weapon = 'wrench'
        elif len(self.game_state.weapons) == 1:
            weapon = random.choice(self.game_state.weapons)
        else:
            weapon = random.choice([weap for weap in self.game_state.weapons if weap != self.game_state.player.weapon])
        self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': weapon}})])
        self.game_state.player.weapon = weapon

    def process_shot_fired(self, src_player, packet_data):

        # Player is Alive, and the teammate who shot was on the enemy team. The object hit was us.
        # ---- N60, Rocket, Flux
        if not self.game_state.player.is_dead and self.game_state.players[src_player].team != self.game_state.player.team and packet_data.object_id == self.game_state.player.player_id:

            # If the opposite player is ALSO a CPU, we need to check the distance to ensure that they are close enough to do dmg
            if self.game_state.players[src_player].username[0:3] == 'CPU' and calculate_distance(self.game_state.player.coord, self.game_state.players[src_player].coord) > self.cpu_damage_min_dist:
                return

            self._model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])

            if packet_data.weapon == 'flux':
                self.game_state.player.health -= 87
                self._model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])
            elif packet_data.weapon == 'n60':
                self.game_state.player.health -= 5
                self._model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])
            elif packet_data.weapon == 'rocket':
                self.game_state.player.health -= 60
                self._model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])
            else:
                return

            self.check_if_dead(src_player, packet_data)

        # ---- Gravity, Blitz, Lava
        elif not self.game_state.player.is_dead and self.game_state.players[src_player].team != self.game_state.player.team and packet_data.weapon in ('grav', 'lava', 'blitz'):
            # Check that the enemy player is within distance to hit us
            if calculate_distance(self.game_state.player.coord, self.game_state.players[src_player].coord) < self.cpu_damage_min_dist:
                # Randomly take hit
                if random.random() < self._close_weapon_self_dmg_rate[packet_data.weapon]:
                    self.game_state.player.health -= self._close_weapon_self_dmg_amount[packet_data.weapon]
                    self._model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])
                    self.check_if_dead(src_player, packet_data)
            else: # player out of range
                pass


    def check_if_dead(self, src_player, packet_data):
        # ---- Process health now
        if self.game_state.player.health < 0:

            self.game_state.player.is_dead = True
            self.game_state.player.animation = None

            # Aquatos Sewers
            test_map = {
                0: '01',
                1: '03',
                2: '06',
                3: '09',
                4: '0C',
                5: '0F',
                6: '12',
                7: '15'
            }
            # Death animation
            #self._model._tcp.queue(rtpacket_to_bytes(ClientAppBroadcastSerializer.build(hex_to_bytes(f"00030001{test_map[self.game_state.player.player_id]}000700000000"))))
            self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'src': self.game_state.player.player_id, 'num_messages': 1, 'msg0': {'type': 'health_update', 'health': 0}})])

            self._model.dmetcp_queue.put(['B', tcp_0204_player_killed.tcp_0204_player_killed(killer_id=src_player, killed_id=self.game_state.player.player_id, weapon=packet_data.weapon)])

            self.game_state.player.respawn_time = datetime.now().timestamp() + self.respawn_time




    def __str__(self):
        return "prototype class"
