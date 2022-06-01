from collections import deque
from butils.utils import *
import os

from constants.constants import TEAM_MAP, SKIN_MAP, WEAPON_MAP

player_id_map = {
    '0000': -1,
    '0100': 0,
    '0300': 1,
    '0600': 2,
    '0900': 3,
    '0C00': 4,
    '0F00': 5,
    '1200': 6,
    '1500': 7,
}
'''
0003
00
01
0100
0A
F8CA
'''
class tcp_0003_broadcast_lobby_state:
    def __init__(self, data:dict):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x03'
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        # Length is #messages * 17
        packet = {}
        packet['base_type'] = data.popleft()
        assert packet['base_type'] in {'01', '00'}
        packet['num_messages'] = bytes_to_int_little(hex_to_bytes(data.popleft()))
        if packet['num_messages'] != 1:
            packet['num_messages'] -= 1

        packet['src'] = player_id_map[data.popleft() + data.popleft()]

        for i in range(packet['num_messages']):
            sub_message = {}

            if len(data) == 0:
                break
            broadcast_type = data.popleft()

            if broadcast_type == '05': # Ready/Unready
                ready_unready_map = {'00': 'unready', '06': 'ready', '05': 'kicked', '06': 'unk_06_loading_in', '07': 'unk_07_loading_in', '08': 'unk_08_in_game'}
                sub_message['type'] = 'ready/unready'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = ready_unready_map[val]
            elif broadcast_type == '03': # Color
                sub_message['type'] = 'colors'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = TEAM_MAP[val]
            elif broadcast_type == '02': # Skins
                sub_message['type'] = 'skins'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = SKIN_MAP[val]
            elif broadcast_type == '07':
                sub_message['type'] = '07_timer_update'
                sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
            elif broadcast_type == '09':
                sub_message['type'] = '09_timer_update'
                if len(data) == 2:
                    sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(2)]))
                else:
                    sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
            elif broadcast_type == '0D':
                sub_message['type'] = 'unk_0D'
                sub_message['unk2'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
            elif broadcast_type == '0A':
                sub_message['type'] = 'weapon_update'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(5)])
                packet[f'msg{i}'] = sub_message
            elif broadcast_type == '00':
                if len(data) == 3:
                    sub_message['type'] = 'unk00'
                    sub_message['unk1'] = ''.join([data.popleft() for i in range(3)])
                else:
                    sub_message['type'] = 'settings_update'
                    sub_message['unk1'] = ''.join([data.popleft() for i in range(283)])
                packet[f'msg{i}'] = sub_message
            elif broadcast_type == '08':
                sub_message['type'] = 'weapon_changed'
                weap_changed_to = data.popleft()
                if weap_changed_to == '00':
                    sub_message['weapon_changed_to'] = 'NA'
                else:
                    sub_message['weapon_changed_to'] = WEAPON_MAP[weap_changed_to]

                sub_message['unk1'] = ''.join([data.popleft() for i in range(3)])
            else:
                raise Exception(f'{broadcast_type} not known!')

            packet[f'msg{i}'] = sub_message

        return tcp_0003_broadcast_lobby_state(packet)

    def to_bytes(self):
        if self.data['msg0']['type'] == 'weapon_changed':
            # 01 is the unk1
            return self.id + \
                hex_to_bytes('00') + \
                int_to_bytes_little(1, self.data['num_messages']) + \
                hex_to_bytes({v: k for k, v in player_id_map.items()}[self.data['src']]) + \
                hex_to_bytes('08') + \
                hex_to_bytes({v: k for k, v in WEAPON_MAP.items()}[self.data['msg0']['weapon_changed_to']]) + \
                hex_to_bytes("000000")

        elif self.data['msg0']['type'] == '09_timer_update':
            # 01 is the unk1
            return self.id + \
                hex_to_bytes('00') + \
                int_to_bytes_little(1, self.data['num_messages']) + \
                hex_to_bytes({v: k for k, v in player_id_map.items()}[self.data['src']]) + \
                hex_to_bytes('09') + \
                int_to_bytes_little(4, self.data['msg0']['time'])
        elif self.data['msg0']['type'] == 'unk_0D':
            # 01 is the unk1
            return self.id + \
                hex_to_bytes('00') + \
                int_to_bytes_little(1, self.data['num_messages']) + \
                hex_to_bytes({v: k for k, v in player_id_map.items()}[self.data['src']]) + \
                hex_to_bytes('0D') + \
                int_to_bytes_little(4, self.data['msg0']['unk2'])
        else:
            raise Exception()

    def __str__(self):
        return f"{self.name}; data:{self.data}"
