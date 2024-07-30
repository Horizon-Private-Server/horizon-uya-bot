import logging
logger = logging.getLogger('thug.object_manager')
logger.setLevel(logging.INFO)

import asyncio

from model.objects.flag import Flag
from model.objects.crate import Crate
from model.objects.healthcrate import HealthCrate

from medius.dme_packets import *
from butils.utils import *

OBJECT_TYPES = {
    'marcadia_palace': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
    },
    'command_center': {
        '131000F7': 'red_flag',
        '141000F7': 'blue_flag',
    },
    'aquatos_sewers': {
        '121000F7': 'red_flag',
        '131000F7': 'blue_flag',
    },
    'blackwater_docks': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
    },
    'bakisi_isles': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
    },
}


class ObjectManager():
    def __init__(self, model, game_state, map:str, game_mode:str):
        self.model = model
        self.game_state = game_state
        self.map = map

        # ['Siege', 'CTF', 'Deathmatch']
        self.game_mode = game_mode

        if self.game_mode == 'CTF':
            self.red_flag = Flag(self.model, 'red', self.map)
            self.blue_flag = Flag(self.model, 'blue', self.map)
        else:
            self.red_flag = None
            self.blue_flag = None
        
        # Object ID -> Crate
        self.health_crates = dict()

        if self.map == 'marcadia_palace':
            self.health_crates['101000F7'] = HealthCrate(self.model, 'Red Base Health', '101000F7', [33415, 56406, 7413])
            self.health_crates['0F1000F7'] = HealthCrate(self.model, 'Blue Base Health', '0F1000F7', [27835, 56425, 7413])
            self.health_crates['0E1000F7'] = HealthCrate(self.model, 'Turret Health', '0E1000F7', [30627, 56543, 7594])

    def reset_all_masters(self):
        # Reset all the masters of all objects to P0
        logger.info(f"Resetting object masters ...")

        for crate in self.health_crates.values():
            crate.owner = 0
            crate.master = 0
            data = {'new_owner': crate.owner, 'counter': crate.counter, 'master': crate.master, 'object_id': crate.id}
            logger.info(f"Resetting crate: {data}")

            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p0_change_owner_req', timestamp=self.game_state.player.time,data=data)])

            data = {'object_id': crate.id, 'counter': crate.counter, 'master': 0}
            self.model.dmetcp_queue.put([0, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])

        if self.red_flag != None or self.blue_flag != None:

            self.red_flag.owner = 0
            self.red_flag.master = 0
            self.blue_flag.owner = 0
            self.blue_flag.master = 0


            logger.info(f"Resetting flag: {data}")
            data = {'new_owner': self.red_flag.owner, 'counter': self.red_flag.counter, 'master': self.red_flag.master, 'object_id': self.red_flag.id}
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p0_change_owner_req', timestamp=self.game_state.player.time,data=data)])

            data = {'object_id': self.red_flag.id, 'counter': self.red_flag.counter, 'master': 0}
            self.model.dmetcp_queue.put([0, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])

            logger.info(f"Resetting flag: {data}")
            data = {'new_owner': self.blue_flag.owner, 'counter': self.blue_flag.counter, 'master': self.blue_flag.master, 'object_id': self.blue_flag.id}
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p0_change_owner_req', timestamp=self.game_state.player.time,data=data)])

            data = {'object_id': self.blue_flag.id, 'counter': self.blue_flag.counter, 'master': 0}
            self.model.dmetcp_queue.put([0, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])

    def loop_update(self):
        # We need to check the positions of each player in comparison to each object
        for player_id, player in self.model.game_state.players.items():
            for crate_id, crate in self.health_crates.items():
                # We don't need to process if we aren't the owner
                if crate.owner != self.game_state.player.player_id or crate.respawning == True:
                    continue

                if crate.overlap(player.coord):
                    # Send out object pickup
                    data = {'player_who_picked_up': player_id}
                    self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_object_pickup', object_type=crate_id,timestamp=self.game_state.player.time,data=data)])
                    self.model.loop.create_task(self.health_crates[crate_id].respawn())
                    self.model.game_state.players[player_id].reset_health()

            # Flag Saves
            if self.red_flag != None and self.red_flag.overlap(player.coord) and not self.red_flag.is_at_base() and self.red_flag.holder == None and self.red_flag.owner == self.game_state.player.player_id and player.team == 'red' and not player.is_dead:
                # Save the flag
                self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.red_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{player_id}_flag_save'})])
                self.red_flag.reset()

            elif self.blue_flag != None and self.blue_flag.overlap(player.coord) and not self.blue_flag.is_at_base() and self.blue_flag.holder == None and self.blue_flag.owner == self.game_state.player.player_id and player.team == 'blue' and not player.is_dead:
                # Save the flag
                self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.blue_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{player_id}_flag_save'})])
                self.blue_flag.reset()

            # Flag Pickup
            #logger.info(f"Check self.red_flag.overlap(player.coord):{self.red_flag.overlap(player.coord)} self.red_flag.holder == None:{self.red_flag.holder == None} self.red_flag.owner == self.game_state.player.player_id:{self.red_flag.owner == self.game_state.player.player_id} player.team == 'blue':{player.team == 'blue'}")
            if self.red_flag != None and self.red_flag.overlap(player.coord) and self.red_flag.holder == None and self.red_flag.owner == self.game_state.player.player_id and player.team == 'blue' and not self.red_flag.is_recent_drop() and not player.is_dead:
                player_id_hex = bytes_to_hex(int_to_bytes_little(4, player_id))
                self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_object_update', object_type=self.red_flag.id,timestamp=self.model.game_state.player.time,data={'object_update_unk': player_id_hex})])
                self.red_flag.holder = self.game_state.player.player_id
            elif self.blue_flag != None and self.blue_flag.overlap(player.coord) and self.blue_flag.holder == None and self.blue_flag.owner == self.game_state.player.player_id and player.team == 'red' and not self.blue_flag.is_recent_drop() and not player.is_dead:
                player_id_hex = bytes_to_hex(int_to_bytes_little(4, player_id))
                self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_object_update', object_type=self.blue_flag.id,timestamp=self.model.game_state.player.time,data={'object_update_unk': player_id_hex})])
                self.blue_flag.holder = self.game_state.player.player_id

        # Check if the bot has saved the flag
        if self.red_flag != None and self.red_flag.overlap(self.game_state.player.coord) and not self.red_flag.is_at_base() and self.red_flag.holder == None and self.red_flag.owner == self.game_state.player.player_id and self.game_state.player.team == 'red' and not self.game_state.player.is_dead:
            # Save the flag
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.red_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{self.game_state.player.player_id}_flag_save'})])
            self.red_flag.reset()

        elif self.blue_flag != None and self.blue_flag.overlap(self.game_state.player.coord) and not self.blue_flag.is_at_base() and self.blue_flag.holder == None and self.blue_flag.owner == self.game_state.player.player_id and self.game_state.player.team == 'blue' and not self.game_state.player.is_dead:
            # Save the flag
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.blue_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{self.game_state.player.player_id}_flag_save'})])
            self.blue_flag.reset()

        # Check if we picked it up
        # TODO: State transition to holding flag
        if self.red_flag != None and self.red_flag.overlap(self.game_state.player.coord) and self.red_flag.holder == None and self.red_flag.owner == self.game_state.player.player_id and self.game_state.player.team == 'blue' and not self.red_flag.is_recent_drop() and not self.game_state.player.is_dead:
            # Red flag pickup as blue team
            player_id_hex = bytes_to_hex(int_to_bytes_little(4, self.game_state.player.player_id))
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_object_update', object_type=self.red_flag.id,timestamp=self.model.game_state.player.time,data={'object_update_unk': player_id_hex})])
            self.red_flag.holder = self.game_state.player.player_id
        elif self.blue_flag != None and self.blue_flag.overlap(self.game_state.player.coord) and self.blue_flag.holder == None and self.blue_flag.owner == self.game_state.player.player_id and self.game_state.player.team == 'red' and not self.blue_flag.is_recent_drop() and not self.game_state.player.is_dead:
            # Red flag pickup as blue team
            player_id_hex = bytes_to_hex(int_to_bytes_little(4, self.game_state.player.player_id))
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_object_update', object_type=self.blue_flag.id,timestamp=self.model.game_state.player.time,data={'object_update_unk': player_id_hex})])
            self.blue_flag.holder = self.game_state.player.player_id    

        # Capture flag
        if self.red_flag != None and self.game_state.player.team == 'blue' and self.blue_flag.is_capture(self.game_state.player.coord) and self.red_flag.holder == self.game_state.player.player_id and not self.game_state.player.is_dead:
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.red_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{player_id}_capture'})])
            self.red_flag.reset()
        elif self.blue_flag != None and self.game_state.player.team == 'red' and self.red_flag.is_capture(self.game_state.player.coord) and self.blue_flag.holder == self.game_state.player.player_id and not self.game_state.player.is_dead:
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=self.blue_flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'p{player_id}_capture'})])
            self.blue_flag.reset()


    def object_update(self, src_player:int, dme_packet):
        logger.info(f"Object update: {src_player} | {dme_packet}")

        if dme_packet.subtype[2:] == '_crate_destroyed':
            pass # We don't care if just the box was broken

        elif dme_packet.subtype[2:] == '_object_pickup':
            if dme_packet.object_type not in self.health_crates:
                logger.warning(f"Unknown object id on object pickup (from {src_player}): {dme_packet}")
            else: # Picked up health
                if dme_packet.data['player_who_picked_up'] == self.model.game_state.player.player_id:
                    self.model.game_state.player.reset_health()
                else:
                    self.model.game_state.players[dme_packet.data['player_who_picked_up']].reset_health()
                self.model.loop.create_task(self.health_crates[dme_packet.object_type].respawn())

        elif dme_packet.subtype[2:] == '_crate_destroyed_and_pickup':
            if dme_packet.object_type not in self.health_crates:
                logger.warning(f"Unknown object id on object crate_destroyed_and_pickup (from {src_player}): {dme_packet}")
            else:
                self.model.loop.create_task(self.health_crates[dme_packet.object_type].respawn())

        elif dme_packet.subtype[2:] == '_change_owner_req':
            if dme_packet.data['object_id'] not in self.health_crates and (self.red_flag != None and dme_packet.data['object_id'] != self.red_flag.id) and (self.blue_flag != None and dme_packet.data['object_id'] != self.blue_flag.id):
                logger.warning(f"Unknown object id on change owner request (from {src_player}): {dme_packet}")
            elif dme_packet.data['object_id'] in self.health_crates:
                self.health_crates[dme_packet.data['object_id']].owner = dme_packet.data['new_owner']
                self.health_crates[dme_packet.data['object_id']].counter = dme_packet.data['counter']
                data = {'object_id': dme_packet.data['object_id'], 'counter': self.health_crates[dme_packet.data['object_id']].counter, 'master': self.health_crates[dme_packet.data['object_id']].master}
                self.model.dmetcp_queue.put([src_player, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])
            elif self.red_flag != None and dme_packet.data['object_id'] == self.red_flag.id:
                self.red_flag.owner = dme_packet.data['new_owner']
                self.red_flag.counter = dme_packet.data['counter']
                data = {'object_id': dme_packet.data['object_id'], 'counter': self.red_flag.counter, 'master': self.red_flag.master}
                self.model.dmetcp_queue.put([src_player, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])            
            elif self.blue_flag != None and dme_packet.data['object_id'] == self.blue_flag.id:
                self.blue_flag.owner = dme_packet.data['new_owner']
                self.blue_flag.counter = dme_packet.data['counter']
                data = {'object_id': dme_packet.data['object_id'], 'counter': self.blue_flag.counter, 'master': self.blue_flag.master}
                self.model.dmetcp_queue.put([src_player, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])   

        elif dme_packet.subtype[2:] == '_assign_to':
            if dme_packet.data['object_id'] not in self.health_crates and (self.red_flag != None and dme_packet.data['object_id'] != self.red_flag.id) and (self.blue_flag != None and dme_packet.data['object_id'] != self.blue_flag.id):
                logger.warning(f"Unknown object id on assign_to (from {src_player}): {dme_packet}")
            elif dme_packet.data['object_id'] in self.health_crates:
                self.health_crates[dme_packet.data['object_id']].owner = self.model.game_state.player.player_id
                self.health_crates[dme_packet.data['object_id']].counter = dme_packet.data['counter']
            elif self.red_flag != None and dme_packet.data['object_id'] == self.red_flag.id:
                self.red_flag.owner = self.model.game_state.player.player_id
                self.red_flag.counter = dme_packet.data['counter']
            elif self.blue_flag != None and dme_packet.data['object_id'] == self.blue_flag.id:
                self.blue_flag.owner = self.model.game_state.player.player_id
                self.blue_flag.counter = dme_packet.data['counter']

        elif dme_packet.subtype[2:] == '_flag_update' and (dme_packet.data['flag_update_type'][2:] == '_flag_save' or dme_packet.data['flag_update_type'] == 'flag_return'):
            # Flag Save by player or timeout
            if dme_packet.object_type == self.red_flag.id:
                self.red_flag.reset()
            elif dme_packet.object_type == self.blue_flag.id:
                self.blue_flag.reset()

        elif dme_packet.subtype[2:] == '_flag_update' and dme_packet.data['flag_update_type'][2:] == '_capture':
            # Flag Capture
            if dme_packet.object_type == self.red_flag.id:
                self.game_state.blue_caps += 1
                self.red_flag.reset()
            elif dme_packet.object_type == self.blue_flag.id:
                self.game_state.red_caps += 1
                self.blue_flag.reset()

        elif dme_packet.subtype[2:] == '_object_update':
            ### Flag Pickup
            if dme_packet.object_type == self.red_flag.id:
                player_who_picked_up = hex_to_int_little(dme_packet.data['object_update_unk'])
                # Set the player to be holding the flag
                self.red_flag.holder = player_who_picked_up
            elif dme_packet.object_type == self.blue_flag.id:
                player_who_picked_up = hex_to_int_little(dme_packet.data['object_update_unk'])
                self.blue_flag.holder = player_who_picked_up

        elif dme_packet.subtype[2:] == '_flag_drop':
            ### Flag Drop
            location = [dme_packet.data['local_x'], dme_packet.data['local_y'], dme_packet.data['local_z']]
            location = self.game_state.map.transform_local_to_global(location)
            if dme_packet.object_type == self.red_flag.id:
                self.red_flag.dropped(location)
                # Create timeout task 
                self.model.loop.create_task(self.check_flag_timeout('red'))

            elif dme_packet.object_type == self.blue_flag.id:
                self.blue_flag.dropped(location)
                # Create timeout task 
                self.model.loop.create_task(self.check_flag_timeout('blue'))


    async def check_flag_timeout(self, color):
        if color == 'red':
            flag = self.red_flag
        elif color == 'blue':
            flag = self.blue_flag

        initial_flag_drop_pos = flag.location
        await asyncio.sleep(30)

        if color == 'red':
            flag = self.red_flag
        elif color == 'blue':
            flag = self.blue_flag

        if flag.location == initial_flag_drop_pos and flag.holder == None and flag.owner == self.game_state.player.player_id:
            # Flag return
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_flag_update', object_type=flag.id,timestamp=self.model.game_state.player.time,data={'flag_update_type': f'flag_return'})])
            flag.reset()

    def __str__(self):
        result = '\nObjectManager:\n'

        for crate in self.health_crates.values():
            result += str(crate) + '\n'

        if self.red_flag != None or self.blue_flag != None:
            result += str(self.red_flag) + '\n'
            result += str(self.blue_flag) + '\n'

        result = result.strip()
        return result