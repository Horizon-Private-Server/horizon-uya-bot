from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class PlayerConnectedSerializer:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 4, 'cast': bytes_to_int_little}, # Seems to always be 02000000
        {'name': 'src_player', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk2', 'n_bytes': 4, 'cast': bytes_to_int_little}, # C0000264
        {'name': 'unk3', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 65180000
        {'name': 'unk4', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 00000000
        {'name': 'unk5', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 98500000
        {'name': 'unk6', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 01000000
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, player_count=1):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x18'},
        ]
        return packet
