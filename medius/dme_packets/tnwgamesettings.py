from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tnwGameSettingsSerializer:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 36, 'cast': None},
        {'name': 'p0_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p1_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p2_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p3_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p4_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p5_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p6_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p7_username', 'n_bytes': 16, 'cast': bytes_to_str},
        {'name': 'p0_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p1_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p2_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p3_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p4_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p5_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p6_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'p7_clan_tag', 'n_bytes': 8, 'cast': bytes_to_str},
        {'name': 'unk2', 'n_bytes': 144, 'cast': None},
        {'name': 'p0_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p1_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p2_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p3_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p4_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p5_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p6_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p7_bolt_modifier', 'n_bytes': 4, 'cast': None},
        {'name': 'p0_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p1_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p2_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p3_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p4_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p5_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p6_bolt_skill', 'n_bytes': 4, 'cast': None},
        {'name': 'p7_bolt_skill', 'n_bytes': 4, 'cast': None}
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, player_count=1):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x04'},
        ]
        return packet
