from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tcp_0016_player_connect_handshake:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        # {'name': 'unk3', 'n_bytes': 1, 'cast': bytes_to_int_little}, # 05 or 03
        # {'name': 'src_player?_2', 'n_bytes': 1, 'cast': bytes_to_int_little},
        # {'name': 'unk4', 'n_bytes': 2, 'cast': bytes_to_int_little}, # 0300
        # {'name': 'dst_player?_1', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 01000000
        # {'name': 'dst_player?_2', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 01000000
        # {'name': 'unk5', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 00000000
        {'name': 'data', 'n_bytes': 16, 'cast': bytes_to_hex}
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, data):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x16'},
            {'data': hex_to_bytes(data)}
        ]
        return packet
