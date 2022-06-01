import asyncio
import random
from scipy.spatial import distance
from datetime import datetime

from constants.constants import ANIMATION_MAP
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

        self.game_state.player.coord = self.game_state.map.get_random_coord()
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
            'grav': 60,
            'blitz': 20,
            'lava': 38
        }

    async def main_loop(self):
        while self._model.alive:
            try:
                # print(self.game_state)
                # print(self.game_state.weapons)
                # print(self.game_state.game_info)

                # Wait for players to join
                if len(self.game_state.players) == 0:
                    await asyncio.sleep(0.03)
                    continue

                # Randomly pick a valid weapon
                if self.game_state.player.weapon == None:
                    self.change_weapon()

                # Respawn
                if self.game_state.player.is_dead and datetime.now().timestamp() > self.game_state.player.respawn_time:
                    self.game_state.player.weapon = None
                    self.game_state.player.reset_health()
                    self._model.dmetcp_queue.put(['B', tcp_020A_player_respawned.tcp_020A_player_respawned(src_player=self.game_state.player.player_id, map=self.game_state.map.map)])
                    self.game_state.player.coord = self.game_state.map.get_random_coord()
                    self.game_state.player.is_dead = False

                # update angle/coord
                if not self.game_state.player.is_dead:
                    if self.game_state.player.movement_packet_num % 4 == 0:


                        self.tracking = self._model.get_closest_enemy_player()

                        # if we are at 300 distance, we can strafe around instead of walking toward them
                        if calculate_distance(self.game_state.player.coord, self.tracking.coord) > 600 or self.follow_player == True:
                            new_coord = self.game_state.map.path(self.game_state.player.coord, self.tracking.coord)
                        else:
                            new_coord = self.game_state.map.get_random_coord_connected(self.game_state.player.coord)

                        if new_coord[2] > self.game_state.player.coord[2]:
                            self.game_state.player.animation = 'jump'
                        elif new_coord != self.game_state.player.coord:
                            self.game_state.player.animation = 'forward'
                        else:
                            self.game_state.player.animation = None

                        self.game_state.player.coord = new_coord

                # Update camera angle
                if self.game_state.player.movement_packet_num % 5 == 0:
                    self.game_state.player.x_angle = calculate_angle(self.game_state.player.coord, self.tracking.coord)

                # Fire weapon
                #self.fire_weapon()

                # Update movement
                self.send_movement()

                # Sleep for the loop
                await asyncio.sleep(0.03)
            except:
                logger.exception("PROTOTYPE ERROR")
                self._model.alive = False
                break

    def fire_weapon(self):
        if self.arsenal.enabled == False or self.game_state.player.is_dead or self.game_state.weapons == [] or self.game_state.player.weapon in [None, 'wrench']:
            return

        if datetime.now().timestamp() - self.weapon_switch_dt < self.weapon_switch_fire_cooldown:
            return

        weapon_fired_bool, hit_bool = self.arsenal.fire_weapon(self.game_state.player.weapon)

        if weapon_fired_bool:
            # Weapon was fired.

            if hit_bool: # player was hit
                object_id=self.tracking.player_id
            else:
                object_id=-1
            self._model.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(map=self.game_state.map.map, weapon=self.game_state.player.weapon,src_player=self.game_state.player.player_id,time=self.game_state.player.time, object_id=object_id, unk1='08', unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])

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
                self.game_state.player.health -= 20
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

            self._model.dmetcp_queue.put(['B', tcp_0204_player_killed.tcp_0204_player_killed(killer_id=src_player, killed_id=self.game_state.player.player_id, weapon=packet_data.weapon)])

            self.game_state.player.respawn_time = datetime.now().timestamp() + self.respawn_time



    def send_movement(self):
        packet_num = self.game_state.player.gen_packet_num()

        data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': self.game_state.player.x_angle, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': self.game_state.player.x_angle, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': self.game_state.player.x_angle, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': self.game_state.player.x_angle, 'buffer': '00', 'coord': self.game_state.player.coord, 'packet_num': packet_num, 'flush_type': 0, 'last': '7F7F7F7F7F7F7F7F', 'type': 'movement'}

        if self.game_state.player.animation != None:
            data['flush_type'] = 16
            data['animation'] = self.game_state.player.animation

        self._model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

        # God mode
        # self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])
        #
        # self._model.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])



    def __str__(self):
        return "prototype class"
