from collections import deque
import os
from butils.utils import *
from constants.constants import TEAM_MAP, SKIN_MAP



class tcp_0004_tnw:
    def __init__(self, tnw_type:str='', data:dict={}):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x04'
        self.tnw_type = tnw_type
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        packet = {}
        packet['unk1'] = ''.join([data.popleft() for _ in range(20)])

        # Read a string. This will tell us what the type is
        hex_str = ''
        while True:
            latest = data.popleft()
            if latest == '00':
                break
            hex_str += latest
        packet_type = hex_to_str(hex_str)

        if packet_type == 'tNW_GameSetting':
            self.process_tnwgamesetting(packet, data)
        elif packet_type == 'tNW_PlayerData':
            self.process_tnwplayerdata(packet, data)
        else:
            raise Exception()

        return tcp_0004_tnw(packet_type, packet)

    def to_bytes(self):
        if self.tnw_type == 'tNW_PlayerData':
            return self.id + \
                hex_to_bytes(self.data['unk1']) + \
                str_to_bytes("tNW_PlayerData", 15) + \
                hex_to_bytes(self.data['unk2']) + \
                int_to_bytes_little(4, self.data['player_start_time_1']) + \
                hex_to_bytes(self.data['unk3']) + \
                int_to_bytes_little(4, self.data['account_id_1']) + \
                hex_to_bytes(self.data['unk4']) + \
                int_to_bytes_little(4, self.data['player_start_time_2']) + \
                int_to_bytes_little(2, self.data['account_id_2']) + \
                hex_to_bytes(self.data['unk5']) + \
                hex_to_bytes({v: k for k, v in TEAM_MAP.items()}[self.data['team']]) + \
                hex_to_bytes(self.data['unk6'])

        raise Exception()

    def __str__(self):
        return f"{self.name}; tnw_type:{self.tnw_type} data:{self.data}"

    @classmethod
    def process_tnwplayerdata(self, packet, data):
        packet['unk2'] = ''.join([data.popleft() for _ in range(29)])
        packet['player_start_time_1'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        packet['unk3'] = ''.join([data.popleft() for _ in range(20)])
        packet['account_id_1'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        packet['unk4'] = ''.join([data.popleft() for _ in range(20)])
        packet['player_start_time_2'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        packet['account_id_2'] = hex_to_int_little(''.join([data.popleft() for _ in range(2)]))
        packet['unk5'] = ''.join([data.popleft() for _ in range(10)])
        packet['team'] = TEAM_MAP[data.popleft()]
        packet['unk6'] = ''.join([data.popleft() for _ in range(67)])

        # 0000000002D300000100C6BF9A7C260000000000744E575F506C61796572446174610041029A0F44D0C176435C924843000000000000000000000000D8EA14408A7C260000000000000000000000000000000000000000000100000001000000000000000000000000000000D8EA14408A7C2600010000000100000000000000000000000000704100000000000000000000000000000000000000000000010000000000000001000000010000000000000000000000320000005F000000320000000100

    @classmethod
    def process_tnwgamesetting(self, packet, data):
        packet['p0_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p1_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p2_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p3_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p4_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p5_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p6_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        packet['p7_username'] = hex_to_str(''.join([data.popleft() for _ in range(16)]))

        packet['p0_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p1_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p2_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p3_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p4_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p5_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p6_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        packet['p7_clan_tag'] = hex_to_str(''.join([data.popleft() for _ in range(8)]))

        packet['p0_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p1_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p2_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p3_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p4_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p5_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p6_skin'] = SKIN_MAP[data.popleft()]; data.popleft()
        packet['p7_skin'] = SKIN_MAP[data.popleft()]; data.popleft()

        packet['p0_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p1_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p2_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p3_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p4_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p5_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p6_team'] = TEAM_MAP[data.popleft()]; data.popleft()
        packet['p7_team'] = TEAM_MAP[data.popleft()]; data.popleft()

        packet['unk2'] = ''.join([data.popleft() for _ in range(63)])
        packet['nodes'] = data.popleft() == '01'
        packet['unk3'] = ''.join([data.popleft() for _ in range(48)])

        packet['p0_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p1_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p2_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p3_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p4_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p5_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p6_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])
        packet['p7_bolt_modifier'] = ''.join([data.popleft() for _ in range(4)])

        packet['p0_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p1_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p2_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p3_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p4_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p5_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p6_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
        packet['p7_bolt_skill'] = ''.join([data.popleft() for _ in range(4)])
