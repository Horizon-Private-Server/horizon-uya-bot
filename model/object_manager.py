import logging
logger = logging.getLogger('thug.object_manager')
logger.setLevel(logging.INFO)

from model.objects.flag import Flag
from model.objects.crate import Crate
from model.objects.healthcrate import HealthCrate

from medius.dme_packets import *

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
            self.red_flag = Flag('red', self.map)
            self.blue_flag = Flag('blue', self.map)
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
        for crate in self.health_crates.values():
            crate.owner = 0
            crate.master = 0
            data = {'new_owner': crate.owner, 'counter': crate.counter, 'master': crate.master, 'object_id': crate.id}
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p0_change_owner_req', timestamp=self.game_state.player.time,data=data)])

            data = {'object_id': crate.id, 'counter': crate.counter, 'master': 0}
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
            if dme_packet.data['object_id'] not in self.health_crates:
                logger.warning(f"Unknown object id on change owner request (from {src_player}): {dme_packet}")
            else:
                self.health_crates[dme_packet.data['object_id']].owner = dme_packet.data['new_owner']
                self.health_crates[dme_packet.data['object_id']].counter = dme_packet.data['counter']
                data = {'object_id': dme_packet.data['object_id'], 'counter': self.health_crates[dme_packet.data['object_id']].counter, 'master': self.health_crates[dme_packet.data['object_id']].master}
                self.model.dmetcp_queue.put([src_player, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])

        elif dme_packet.subtype[2:] == '_assign_to':
            if dme_packet.data['object_id'] not in self.health_crates:
                logger.warning(f"Unknown object id on assign_to (from {src_player}): {dme_packet}")
            else:
                self.health_crates[dme_packet.data['object_id']].owner = self.model.game_state.player.player_id
                self.health_crates[dme_packet.data['object_id']].counter = dme_packet.data['counter']

        # if dme_packet.name == 'tcp_020C_info' and 'req_confirmation' in dme_packet.subtype:
        #     data = {'object_id': dme_packet.data['object_id'], 'unk': dme_packet.data['unk']}
        #     self.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_confirm', timestamp=self.game_state.player.time, object_id='001000F7', data=data)])

        # if dme_packet.name == 'tcp_020C_info' and '_object_update' in dme_packet.subtype:
        #     # Flag Pickup
        #     object = parse_object_id(dme_packet.object_id, map=self.game_state.map.map)
        #     if object == 'red_flag' or object == 'blue_flag':
        #         self.game_state.players[src_player].flag = object

        # if dme_packet.name == 'tcp_020C_info' and 'flag_drop' in dme_packet.subtype:
        #     # Flag Dropped
        #     object = parse_object_id(dme_packet.object_id, map=self.game_state.map.map)
        #     if object == 'red_flag' or object == 'blue_flag':
        #         for player_id in self.game_state.players.keys():
        #             if self.game_state.players[player_id].flag == object:
        #                 self.game_state.players[player_id].flag = None

        # if dme_packet.name == 'tcp_020C_info' and 'flag_update' in dme_packet.subtype:
        #     # Flag Returned or Flag Captured
        #     object = parse_object_id(dme_packet.object_id, map=self.game_state.map.map)
        #     if object == 'red_flag' or object == 'blue_flag':
        #         if '_capture' in dme_packet.data['flag_update_type'] or dme_packet.data['flag_update_type'] == 'flag_return':
        #             # Find players that have redflag/blueflag and set to None
        #             self.game_state.clear_flag(object)

        #self.game_state.object_manager.object_update(src_player, dme_packet)

    def __str__(self):
        result = '\nObjectManager:\n'

        for crate in self.health_crates.values():
            result += str(crate) + '\n'

        result = result.strip()
        return result