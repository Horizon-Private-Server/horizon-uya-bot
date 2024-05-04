import logging
logger = logging.getLogger('thug.object_manager')
logger.setLevel(logging.INFO)

from model.objects.flag import Flag
from model.objects.crate import Crate
#from model.objects.Health import Health

from medius.dme_packets import *

OBJECT_TYPES = {
    'marcadia_palace': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
        '101000F7': 'red_health',
        '0F1000F7': 'blue_health',
        '0E1000F7': 'turret_health',
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
        self.crates = dict()

        if self.map == 'marcadia_palace':
            self.crates['101000F7'] = Crate(self.model, 'Red Base Health', '101000F7')
            self.crates['0F1000F7'] = Crate(self.model, 'Blue Base Health', '0F1000F7')
            self.crates['0E1000F7'] = Crate(self.model, 'Turret Health', '0E1000F7')


    def reset_all_masters(self):
        # Reset all the masters of all objects to P0
        for crate in self.crates.values():
            crate.owner = 0
            crate.master = 0
            data = {'new_owner': crate.owner, 'counter': 1, 'master': crate.master, 'object_id': crate.id}
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p0_change_owner_req', timestamp=self.game_state.player.time,data=data)])


    def object_update(self, src_player:int, dme_packet):
        logger.info(f"Object update: {src_player} | {dme_packet}")
        if dme_packet.subtype[2:] == '_crate_destroyed':
            pass # We don't care if just the box was broken

        elif dme_packet.subtype[2:] == '_object_pickup':
            if dme_packet.object_type not in self.crates:
                logger.warning(f"Unknown object id on object pickup (from {src_player}): {dme_packet}")
            else:
                self.model.loop.create_task(self.crates[dme_packet.object_type].respawn())

        elif dme_packet.subtype[2:] == '_crate_destroyed_and_pickup':
            if dme_packet.object_type not in self.crates:
                logger.warning(f"Unknown object id on object crate_destroyed_and_pickup (from {src_player}): {dme_packet}")
            else:
                self.model.loop.create_task(self.crates[dme_packet.object_type].respawn())

        elif dme_packet.subtype[2:] == '_change_owner_req':
            if dme_packet.data['object_id'] not in self.crates:
                logger.warning(f"Unknown object id on change owner request (from {src_player}): {dme_packet}")
            else:
                self.crates[dme_packet.data['object_id']].owner = dme_packet.data['new_owner']
                data = {'object_id': dme_packet.data['object_id'], 'counter': 1, 'master': self.crates[dme_packet.data['object_id']].master}
                self.model.dmetcp_queue.put([src_player, tcp_020C_info.tcp_020C_info(subtype=f'p{self.game_state.player.player_id}_assign_to', timestamp=self.game_state.player.time,data=data)])

        elif dme_packet.subtype[2:] == '_assign_to':
            if dme_packet.data['object_id'] not in self.crates:
                logger.warning(f"Unknown object id on assign_to (from {src_player}): {dme_packet}")
            else:
                self.crates[dme_packet.data['object_id']].owner = self.model.game_state.player.player_id

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
