from collections import deque
from butils.utils import *
import os

from constants.constants import TEAM_MAP, SKIN_MAP, WEAPON_MAP

HP_MAP ={
    1097859072:100,
    1096810496:93,
    1095761920:86,
    1094713344:80,
    1093664768:73,
    1092616192:66,
    1091567616:60,
    1090519040:53,
    1088421888:46,
    1086324736:40,
    1084227584:33,
    1082130432:26,
    1077936128:20,
    1073741824:13,
    1065353216:6,
    0:0
}

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

weapon_v2_index_map = {
    0: 'lava',
    1: 'mine',
    2: 'grav',
    3: 'rocket',
    4: 'flux',
    5: 'blitz',
    6: 'n60',
    14: 'morph',
}
'''

0003
00
01
0300
120000

'''

class tcp_0003_broadcast_lobby_state:
    def __init__(self, data:dict):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x03'
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        packet = {}
        packet['base_type'] = data.popleft()
        assert packet['base_type'] in {'01', '00'}
        packet['num_messages'] = bytes_to_int_little(hex_to_bytes(data.popleft()))

        packet['src'] = player_id_map[data.popleft() + data.popleft()]

        for i in range(packet['num_messages']):
            sub_message = {}

            if len(data) == 0:
                break
            broadcast_type = data.popleft()

            if broadcast_type == '00': # usernames
                sub_message['type'] = 'usernames'
                sub_message['usernames'] = ''.join([data.popleft() for i in range(128)])

            elif broadcast_type == '01': # clan tags
                sub_message['type'] = 'clan_tags'
                sub_message['clan_tags'] = ''.join([data.popleft() for i in range(64)])

            elif broadcast_type == '02': # Skins
                sub_message['type'] = 'skins'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = SKIN_MAP[val]

            elif broadcast_type == '03': # Color
                sub_message['type'] = 'colors'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = TEAM_MAP[val]

            elif broadcast_type == '04': # Unk
                sub_message['type'] = 'unk_04'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(16)])

            elif broadcast_type == '05': # Ready/Unready
                ready_unready_map = {'00': 'unready', '06': 'ready', '05': 'kicked', '06': 'unk_06_loading_in', '07': 'unk_07_loading_in', '08': 'unk_08_in_game'}
                sub_message['type'] = 'ready/unready'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = ready_unready_map[val]

            elif broadcast_type == '06': # Unk
                sub_message['type'] = 'unk_06'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(18)])

            elif broadcast_type == '07': # Health
                sub_message['type'] = 'health_update'
                raw_hp = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
                sub_message['health'] = HP_MAP[raw_hp] if raw_hp in HP_MAP else 100

            elif broadcast_type == '08': # Weapon Changed
                sub_message['type'] = 'weapon_changed'
                weap_changed_to = data.popleft()
                if weap_changed_to == '00':
                    sub_message['weapon_changed_to'] = 'NA'
                else:
                    sub_message['weapon_changed_to'] = WEAPON_MAP[weap_changed_to]
                sub_message['unk1'] = ''.join([data.popleft() for i in range(3)])

            elif broadcast_type == '09': # Timer
                sub_message['type'] = '09_timer_update'
                if len(data) == 2:
                    sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(2)]))
                else:
                    sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

            elif broadcast_type == '11': # Unk
                sub_message['type'] = 'bolt_modifier'
                sub_message['bolt_modifier'] = ''.join([data.popleft() for i in range(32)])

            elif broadcast_type == '12': # Unk
                sub_message['type'] = 'bolt_skill'
                sub_message['bolt_skill'] = ''.join([data.popleft() for i in range(32)])

            elif broadcast_type == '0A': # Weapon update 0A
                sub_message['type'] = 'weapon_update_0A'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(2)])

            elif broadcast_type == '0B': # Weapon upgrade 0B
                sub_message['type'] = 'weapon_upgraded'
                bitmask = hex_to_bit_string(''.join([data.popleft() for i in range(2)]))
                for weapon_index, weapon_name in weapon_v2_index_map.items():
                    sub_message[weapon_name] = 'v2' if bitmask[weapon_index] == '1' else 'v1'

            elif broadcast_type == '0C': # Weapon update 0C
                sub_message['type'] = 'weapon_update_0C'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(2)])

            elif broadcast_type == '0D': # Cross hair lockon (required for morph)
                sub_message['type'] = 'crosshair_lockon'
                sub_message['unk1'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

            elif broadcast_type == 'FF': # Unk
                sub_message['type'] = 'unk_FF'
                sub_message['unk1'] = ''.join([data.popleft() for i in range(18)])

            else:
                raise Exception(f'{broadcast_type} not known!')

            packet[f'msg{i}'] = sub_message

        return tcp_0003_broadcast_lobby_state(packet)

    def to_bytes(self):

        result = self.id + \
                hex_to_bytes('00') + \
                int_to_bytes_little(1, self.data['num_messages']) + \
                hex_to_bytes({v: k for k, v in player_id_map.items()}[self.data['src']])

        msgs = [key for key in self.data.keys() if key[0:3] == 'msg']

        for msg in msgs:
            if self.data[msg]['type'] == 'weapon_changed':
                # 01 is the unk1
                result += hex_to_bytes('08') + \
                    hex_to_bytes({v: k for k, v in WEAPON_MAP.items()}[self.data[msg]['weapon_changed_to']]) + \
                    hex_to_bytes("000000")

            elif self.data[msg]['type'] == 'weapon_update_0A': ## Charge boots
                # 08C8 -> Charge boots
                result += hex_to_bytes('0A') + hex_to_bytes("08C8")


            elif self.data[msg]['type'] == 'weapon_upgraded': ## Charge boots
                result += hex_to_bytes('0B')
                base_bits = list('0000000000000000')
                for k, v in weapon_v2_index_map.items():
                    if self.data[msg][v] == 'v2':
                        base_bits[k] = '1'
                hex_v2s = bit_string_to_2_bytes_hex(''.join(base_bits))
                result += hex_to_bytes(hex_v2s)

            elif self.data[msg]['type'] == 'weapon_update_0C': ## Charge boots
                # 08C8 -> Charge boots
                result += hex_to_bytes('0C') + hex_to_bytes("08C8")

            elif self.data[msg]['type'] == '09_timer_update':
                # 01 is the unk1
                result += hex_to_bytes('09') + \
                    int_to_bytes_little(4, self.data[msg]['time'])

            elif self.data[msg]['type'] == 'crosshair_lockon':
               result += hex_to_bytes('0D') + \
                    int_to_bytes_little(4, self.data[msg]['unk1'])

            elif self.data[msg]['type'] == 'health_update':
                # 01 is the unk1
                result += hex_to_bytes('07') + \
                    int_to_bytes_little(4, {v: k for k, v in HP_MAP.items()}[self.data[msg]['health']])
            else:
                raise Exception()
            
        return result

    def __str__(self):
        return f"{self.name}; data:{self.data}"
