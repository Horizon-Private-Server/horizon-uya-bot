from collections import deque
import os
from utils.utils import *

team_map = {
    '00': 'blue',
    '01': 'red',
    '02': 'green',
    '03': 'orange',
    '04': 'yellow',
    '05': 'purple',
    '06': 'aqua',
    '07': 'pink',
    'FF': 'NA'
}
skin_map = {
    '00': 'ratchet',
    '01': 'robo',
    '02': 'thug',
    '03': 'tyhrranoid',
    '04': 'blarg',
    '05': 'ninja',
    '06': 'snow man',
    '07': 'bruiser',
    '08': 'gray',
    '09': 'hotbot',
    '0A': 'gladiola',
    '0B': 'evil clown',
    '0C': 'beach bunny',
    '0D': 'robo rooster',
    '0E': 'buginoid',
    '0F': 'branius',
    '10': 'skrunch',
    '11': 'bones',
    '12': 'nefarious',
    '13': 'trooper',
    '14': 'constructobot',
    '15': 'dan',
    'FF': 'NA'
}

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
                int_to_bytes_little(4, self.data['player_start_time2']) + \
                hex_to_bytes(self.data['unk3']) + \
                int_to_bytes_little(4, self.data['player_start_time2']) + \
                hex_to_bytes(self.data['unk4'])
            # return hex_to_bytes("00040000000002D300000100C6BF597D540000000000744E575F506C61796572446174610041029A0F44D0C176435C924843000000000000000000000000D8EA1440487D540000000000000000000000000000000000000000000100000001000000000000000000000000000000D8EA1440487D5400010000000100000000000000000000000000704100000000000000000000000000000000000000000000010000000000000001000000010000000000000000000000320000005F000000320000000100000F000000000000000001000000030000000000704100004141414141414141414141000000")
        raise Exception()

    def __str__(self):
        return f"{self.name}; tnw_type:{self.tnw_type} data:{self.data}"

    @classmethod
    def process_tnwplayerdata(self, packet, data):
        packet['unk2'] = ''.join([data.popleft() for _ in range(29)])
        packet['player_start_time'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        packet['unk3'] = ''.join([data.popleft() for _ in range(44)])
        packet['player_start_time2'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        packet['unk4'] = ''.join([data.popleft() for _ in range(80)])
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

        packet['p0_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p1_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p2_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p3_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p4_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p5_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p6_skin'] = skin_map[data.popleft()]; data.popleft()
        packet['p7_skin'] = skin_map[data.popleft()]; data.popleft()

        packet['p0_team'] = team_map[data.popleft()]; data.popleft()
        packet['p1_team'] = team_map[data.popleft()]; data.popleft()
        packet['p2_team'] = team_map[data.popleft()]; data.popleft()
        packet['p3_team'] = team_map[data.popleft()]; data.popleft()
        packet['p4_team'] = team_map[data.popleft()]; data.popleft()
        packet['p5_team'] = team_map[data.popleft()]; data.popleft()
        packet['p6_team'] = team_map[data.popleft()]; data.popleft()
        packet['p7_team'] = team_map[data.popleft()]; data.popleft()

        packet['unk2'] = ''.join([data.popleft() for _ in range(112)])

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
