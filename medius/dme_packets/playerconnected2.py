from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class PlayerConnected2Serializer:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 1, 'cast': bytes_to_int_little}, # 00
        {'name': 'src_player?_1', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'unk2', 'n_bytes': 72, 'cast': None}, # C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE0016
        {'name': 'unk3', 'n_bytes': 1, 'cast': bytes_to_int_little}, # 05 or 03
        {'name': 'src_player?_2', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'unk4', 'n_bytes': 2, 'cast': bytes_to_int_little}, # 0300
        {'name': 'dst_player?_1', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 01000000
        {'name': 'dst_player?_2', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 01000000
        {'name': 'unk5', 'n_bytes': 4, 'cast': bytes_to_int_little}, # 00000000
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, player_count=1):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x10'},
        ]
        return packet
