import asyncio
import random
from scipy.spatial import distance
from datetime import datetime
from collections import defaultdict

from constants.constants import ANIMATION_MAP, MAIN_BOT_LOOP_TIMER, get_blitz_angle, get_grav_timing
from medius.dme_packets import *
from butils.utils import *
from butils.circularlist import CircularList

from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer


from model.states.training import *
from model.states.dm import *
from model.states.static import *
from model.states.static_shoot import *

import logging
logger = logging.getLogger('thug.model.prototype')
logger.setLevel(logging.INFO)

class Prototype:
    def __init__(self, model, profile, bot_mode, game_state):
        self.model = model
        self.profile = profile
        self.game_state = game_state
        self.bot_mode = bot_mode

        self.target = [0,0,0]

        # self.game_state.player.coord = self.game_state.map.get_respawn_location(self.game_state.player.team, self.game_state.game_mode)
        self.game_state.player.coord = [0,0,0]
        self.game_state.player.x_angle = 127

        self.follow_player = False

        self.cpu_damage_min_dist = 800

        self.respawn_time = 5

        self.weapon_switch_fire_cooldown = .3
        self.weapon_switch_dt = datetime.now().timestamp()

        self.changing_weapons = False

        self._misc = defaultdict(int)


        self.game_state.player.arsenal.weapons['flux']['hit_rate'] = .3
        self.game_state.player.arsenal.weapons['grav']['hit_rate'] = .2

        self.game_state.player.arsenal.update_from_profile(self.profile)

        ###### Set the cycle
        weapon_order_list = list(self.game_state.weapons)
        random.shuffle(weapon_order_list)
        if set(weapon_order_list) == {'blitz', 'flux', 'grav'}:
            weapon_order_list = ['grav', 'flux', 'blitz']
        self.weapon_order = CircularList(weapon_order_list, circular=True, casttype=str)

        self.state = None

        # Warn if we go over this. Normal is 0.068
        self._state_update_max_time = 0.08

    def transition_state(self, new_state:str, msg: dict=dict()):
        logger.info(f"Transitioning from {self.state} to {new_state}")
        self.state.exit()
        self.state = eval(f"{new_state}.{new_state}(self)")
        self.state.enter(msg)

    def state_update(self):
        # If we are dead, don't update.
        if self.game_state.player.is_dead:
            return

        if self.state == None:
            if 'training' in self.bot_mode:
                self.state = training_initial.training_initial(self)
            elif self.bot_mode == 'dynamic':
                if self.game_state.game_mode == 'Deathmatch':
                    self.state = dm_initial.dm_initial(self)
            elif self.bot_mode == 'static':
                self.state = static_initial.static_initial(self)
            elif self.bot_mode == 'static shoot':
                self.state = static_shoot_initial.static_shoot_initial(self)
            self.state.enter({})

        #logger.info(str(self.model.game_state))
        self.state.update()
        return


        target_player_id = 0

        self.target = self.game_state.players[target_player_id].coord

        #self.game_state.player.coord = [32689, 55927, 7413]

        # Quad patrol near red base marcadia
        marc_points = [
            [32939, 54784, 7413],
            [32418, 53872, 7413],
            [31608, 54666, 7413],
            [32540, 55641, 7407],
        ]

        # Moving across map by healthboxes marcadia
        # marc_points = [
        #     [33289, 56515, 7413],
        #     [30680, 56370, 7413],
        #     [27973, 56516, 7413],
        # ]

        self.patrol(marc_points, circular=False)

        self.fire_weapon(object_id = self.game_state.players[target_player_id].player_id)


    async def main_loop(self):
        while self.model.alive:
            try:

                #logger.info(self.game_state)

                state_update_start_time = datetime.now()

                if self.game_state.player.weapon == None:
                    self.set_initial_weapon()

                # Update game objects
                self.game_state.object_manager.loop_update()

                # Respawn
                if self.game_state.player.is_dead and datetime.now().timestamp() > self.game_state.player.respawn_time:
                    self.respawn()

                # Run states
                self.state_update()

                # Send movement
                self.send_movement()

                # Sleep for the loop
                await asyncio.sleep(MAIN_BOT_LOOP_TIMER)

                # Check metrics
                state_update_end_time = datetime.now()
                time_diff = (state_update_end_time - state_update_start_time).total_seconds()
                if time_diff > self._state_update_max_time:
                    logger.warning(f"State update took too long -- off by {round(percent_difference(time_diff, 0.068)):3d}% -- {time_diff:.3f} s")
            except:
                logger.exception("PROTOTYPE ERROR")
                self.model.alive = False
                break


    def send_movement(self):
        if self.game_state.players[0].coord == [0,0,0] or self.game_state.player.is_dead:
            return

        packet_num = self.game_state.player.gen_packet_num()
        data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': self.game_state.player.x_angle, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': self.game_state.player.x_angle, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': self.game_state.player.x_angle, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': self.game_state.player.x_angle, 'buffer': '00', 'coord': self.game_state.player.coord, 'packet_num': packet_num, 'flush_type': 0, 'type': 'movement'}

        if not self.game_state.player.stunned:
            if self.game_state.player.animation != None:
                data['flush_type'] = 16
                data['animation'] = self.game_state.player.animation

            if self.game_state.player.left_joystick_x != None:
                data['left_joystick_x'] = self.game_state.player.left_joystick_x
                data['left_joystick_y'] = self.game_state.player.left_joystick_y

        self.model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

        self.game_state.player.prev_animation = self.game_state.player.animation
        self.game_state.player.animation = None

    def patrol(self, coords, circular=False):
        if 'patrol' not in self._misc.keys():
            self._misc['patrol'] = CircularList(coords, circular=circular)
        elif self._misc['patrol'] != coords:
            self._misc['patrol'] = CircularList(coords, circular=circular)

        if calculate_distance(self.game_state.player.coord, self._misc['patrol'].peek()) > 70:
            patrol_coord = self._misc['patrol'].peek()
        else:
            patrol_coord = self._misc['patrol'].pop()

        new_coord = self.game_state.map.path(self.game_state.player.coord, patrol_coord)
        self.update_joystick_input_and_angle(self.game_state.player.coord, new_coord)
        self.game_state.player.set_coord(new_coord)


    def update_joystick_input_and_angle(self, old_coord, new_coord):
        if self.game_state.player.stunned:
            return

        # Start with no animation
        self.game_state.player.animation = None

        self.game_state.player.x_angle = calculate_angle(new_coord, self.target)
        if old_coord == new_coord:
            self.game_state.player.animation = None
            self.game_state.player.left_joystick_x = None
            self.game_state.player.left_joystick_y = None
            return

        if new_coord[2] > old_coord[2]:
            self.game_state.player.animation = 'jump'

        if self.game_state.player.prev_animation != 'crouch' and calculate_distance(old_coord, new_coord) > 95:
            self.game_state.player.animation = 'crouch'

        angle = compute_strafe_angle(old_coord, new_coord, self.target)
        strafe_direction = get_strafe_direction(old_coord, new_coord, self.target)
        strafe_angle_joystick = strafe_joystick_input(angle, strafe_direction)

        self.game_state.player.left_joystick_x = strafe_angle_joystick[0]
        self.game_state.player.left_joystick_y = strafe_angle_joystick[1]

        # logger.info(f"{self.game_state.player.animation} | {strafe_angle_joystick} | {angle:3.0f} | {strafe_direction}")


    def respawn(self):
        self.game_state.player.weapon = None
        self.game_state.player.reset_health()
        self.model.dmetcp_queue.put(['B', tcp_020A_player_respawned.tcp_020A_player_respawned(src_player=self.game_state.player.player_id, map=self.game_state.map.map)])
        self.game_state.player.set_coord(self.game_state.map.get_respawn_location(self.game_state.player.team, self.game_state.game_mode))
        self.game_state.player.is_dead = False
        
        data_packet = self.game_state.player.arsenal.dump_upgrades()
        data_packet['type'] = 'weapon_upgraded'
        self.model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': data_packet})])

    def fire_weapon(self, object_id=-1):
        if self.game_state.player.arsenal.enabled == False or self.game_state.player.is_dead or self.game_state.weapons == [] or self.game_state.player.weapon in [None, 'wrench', 'hyper'] or self.changing_weapons:
            return

        if datetime.now().timestamp() - self.weapon_switch_dt < self.weapon_switch_fire_cooldown:
            return

        weapon_fired_bool, hit_bool = self.game_state.player.arsenal.fire_weapon(self.game_state.player.weapon)

        if weapon_fired_bool:
            # Weapon was fired.

            local_x = 0
            local_y = 0
            local_z = 0
            local_x_2 = 0
            local_y_2 = 0
            local_z_2 = 0

            if hit_bool: # object was hit
                object_id=object_id
            else:
                object_id=-1

                target_coord = self.target
                if self.game_state.player.weapon == 'grav' and random.random() < self.profile.grav_hit_percent:
                    # We only want to fire next to the player if we are a strong bot
                    local_player_coord = self.game_state.map.transform_global_to_local(target_coord)
                else:
                    # Shoot directly between the two players just slightly forward
                    local_player_coord = self.game_state.map.transform_global_to_local(self.game_state.map.get_front_gbomb_position(self.game_state.player.coord, self.target))

                #print(target_coord, local_player_coord)

                local_x_2 = local_player_coord[0]
                local_y_2 = local_player_coord[1]
                local_z_2 = local_player_coord[2]
                
                if self.game_state.player.weapon == 'blitz':
                    # 1. Get the angle between the player and target
                    x_angle = calculate_angle(self.game_state.player.coord, self.target)
                    # 2. Transform that to local coordinates
                    local_x, local_y = get_blitz_angle(x_angle)

                    local_x_2 = local_x
                    local_y_2 = local_y
                    local_z_2 = 15511 # Forward looking height

                elif self.game_state.player.weapon == 'grav':
                    local_x = local_x_2
                    local_y = local_y_2
                    local_z = local_z_2

            self.model.dmetcp_queue.put(['B', packet_020E_shot_fired.packet_020E_shot_fired(network='tcp', map=self.game_state.map.map, weapon=self.game_state.player.weapon,src_player=self.game_state.player.player_id,time=self.game_state.player.time, object_id=object_id, unk1='08', local_x=local_x, local_y=local_y, local_z=local_z, local_x_2=local_x_2, local_y_2=local_y_2, local_z_2=local_z_2)])


    async def change_weapon_timer(self):
        self.changing_weapons = True
        await asyncio.sleep(.2)
        self.changing_weapons = False

    def change_weapon(self, weapon:str):
        if self.game_state.player.weapon == weapon:
            return

        self.weapon_switch_dt = datetime.now().timestamp()
        self.model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': weapon}})])
        self.game_state.player.weapon = weapon
        self.model.loop.create_task(self.change_weapon_timer())

    def cycle_weapons(self, weapons: list):
        if 'cycle' not in self._misc.keys() or self._misc['cycle'] != weapons:
            self._misc['cycle'] = CircularList(weapons, circular=True, casttype=str)
            self._misc['cycle_change_time'] = datetime.now()

        if (datetime.now() - self._misc['cycle_change_time']).total_seconds() > .5:
            self.change_weapon(self._misc['cycle'].pop())
            self._misc['cycle_change_time'] = datetime.now()


    def process_shot_fired(self, src_player, packet_data):
        #logger.info(self.game_state)
        # Player is Alive, and the teammate who shot was on the enemy team. The object hit was us.
        if self.game_state.player.is_dead or self.game_state.players[src_player].team == self.game_state.player.team:
            return

        damage = 0

        player_distance = calculate_distance(self.game_state.player.coord, self.game_state.players[src_player].coord)


        if packet_data.weapon == 'blitz' and packet_data.unk1 == '08' and player_distance < 2089: # 2089 minimum for 7 damage
            # The player shooting angle needs to be aiming at the player
            angle_needed = calculate_angle(self.game_state.players[src_player].coord, self.game_state.player.coord)
            players_angle = self.game_state.players[src_player].cam_x


            # Make this higher to make it easier to hit
            short_dist_thresh = 60
            long_distance_thresh = 10
            if player_distance > 400 and abs(players_angle - angle_needed) > long_distance_thresh:
                return
            elif player_distance < 400 and abs(players_angle - angle_needed) > short_dist_thresh:
                return


            if player_distance < 245: # 245 minimum for 54 damage
                damage = 54 if self.game_state.players[src_player].arsenal.weapons['blitz']['upgrade'] == 'v1' else 100 #v2
            elif player_distance < 541: # 541 minimum for 26 damage
                damage = 26 if self.game_state.players[src_player].arsenal.weapons['blitz']['upgrade'] == 'v1' else 47 # v2
            elif player_distance < 739: # 739 minimum for 14 damage
                damage = 14 # 
            else:
                damage = 7 if self.game_state.players[src_player].arsenal.weapons['blitz']['upgrade'] == 'v1' else 47 # 14 v2

        elif packet_data.weapon == 'grav' and packet_data.unk1 == '08': # 2089 minimum for 7 damage
            # Get the player's coordinate. Calculate distance of that to 
            src_player_coord = self.game_state.players[src_player].coord

            local_coord = [packet_data.local_x, packet_data.local_y, packet_data.local_z]
            dest_coord = self.game_state.map.transform_local_to_global(local_coord)
            
            dist = calculate_distance(src_player_coord, dest_coord)
            #logger.info(f"Grav bomb explode: {dist} {src_player_coord} | {dest_coord} | {local_coord}")

            time_to_explode = get_grav_timing(dist)

            logger.info(f"Grav bomb explode: {dist} {src_player_coord} | {dest_coord} | {local_coord} | {time_to_explode}")

            if time_to_explode != -1:
                self.model.loop.create_task(self.process_grav_bomb_explode(time_to_explode, dest_coord, src_player, 'grav'))

        # -- Flux
        elif packet_data.object_id == self.game_state.player.player_id:
            # If the opposite player is ALSO a CPU, we need to check the distance to ensure that they are close enough to do dmg
            if self.game_state.players[src_player].username[0:3] == 'CPU' and calculate_distance(self.game_state.player.coord, self.game_state.players[src_player].coord) > 1000:
                return

            if packet_data.weapon == 'flux':
                damage = 87 if self.game_state.players[src_player].arsenal.weapons['flux']['upgrade'] == 'v1' else 100 # v2

        if damage != 0:
            self.game_state.player.take_damage(damage)
            self.model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'src': self.game_state.player.player_id, 'num_messages': 1, 'msg0': {'type': 'health_update', 'health': self.game_state.player.health}})])

            if damage > 10 and self.game_state.player.health > 0:
                self.game_state.player.stunned = True
                self.model.loop.create_task(self.reset_stun())
                self.model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])

            self.check_if_dead(src_player, packet_data.weapon)

    async def reset_stun(self):
        # stun time
        stun_time = .5
        await asyncio.sleep(stun_time)
        self.game_state.player.stunned = False


    async def process_grav_bomb_explode(self, time_to_explode, dest_coord, src_player, weapon):
        await asyncio.sleep(time_to_explode)
        # Check if our player is within distance of explosion
        dist = calculate_distance(dest_coord, self.game_state.player.coord)
        # 460 threshold
        if dist <= 460:
            self.game_state.player.arsenal.reset_upgrades()
            dmg = 60 if self.game_state.players[src_player].arsenal.weapons['grav']['upgrade'] == 'v1' else 94
            self.game_state.player.take_damage(dmg)
            self.game_state.player.animation = None
            self.model.dmeudp_queue.put(['B', udp_020F_player_damage_animation.udp_020F_player_damage_animation(src_player=self.game_state.player.player_id)])
            self.check_if_dead(src_player, weapon)


    def check_if_dead(self, src_player, weapon):
        # ---- Process health now
        if self.game_state.player.health <= 0 and self.game_state.player.is_dead == False:

            self.game_state.player.arsenal.reset_upgrades()

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
            #self.model._tcp.queue(rtpacket_to_bytes(ClientAppBroadcastSerializer.build(hex_to_bytes(f"00030001{test_map[self.game_state.player.player_id]}000700000000"))))
            self.model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'src': self.game_state.player.player_id, 'num_messages': 1, 'msg0': {'type': 'health_update', 'health': 0}})])

            self.model.dmetcp_queue.put(['B', tcp_0204_player_killed.tcp_0204_player_killed(killer_id=src_player, killed_id=self.game_state.player.player_id, weapon=weapon)])

            self.game_state.player.respawn_time = datetime.now().timestamp() + self.respawn_time

            self.game_state.player_killed(src_player)

    def set_initial_weapon(self):
        weapon = 'hyper'
        self.model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': weapon}})])
        self.game_state.player.weapon = weapon

    def __str__(self):
        return "prototype class"
