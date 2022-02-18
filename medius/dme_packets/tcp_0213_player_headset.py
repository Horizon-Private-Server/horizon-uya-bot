from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tcp_0213_player_headset:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 4, 'cast': bytes_to_int_little}
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x02\x13'},
            {'buf': hex_to_bytes('00000000')},
        ]
        return packet
