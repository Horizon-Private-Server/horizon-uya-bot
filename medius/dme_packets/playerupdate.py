from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class PlayerUpdateSerializer:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk2', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk3', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk4', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk5', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'unk6', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk7', 'n_bytes': 14, 'cast': bytes_to_str}, # username
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x0F'},
            {'data': hex_to_bytes('0100000000000000001003000300000000001A0000004242424242424242424242000000')}
        ]
        return packet
