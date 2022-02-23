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

class tcp_0004_tnwgamesettings:
    def __init__(self, data):
        self.name = os.path.basename(__file__)
        self.id = b'\x00\x04'

        self.data = data


    @classmethod
    def serialize(self, data: deque):
        packet = {}
        packet['unk1'] = ''.join([data.popleft() for _ in range(36)])

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

        return tcp_0004_tnwgamesettings(packet)

    def to_bytes(self):
        raise Exception()

    def __str__(self):
        return f"{self.name}; data:{self.data}"
