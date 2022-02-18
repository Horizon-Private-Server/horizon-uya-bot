from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tcp_000F_playername_update:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'time', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'unk1', 'n_bytes': 18, 'cast': None},
        {'name': 'username', 'n_bytes': 11, 'cast': bytes_to_str}, # username
        {'name': 'unk2', 'n_bytes': 3, 'cast': None}
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, time, unk1, username, unk2):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x0F'},
            {'time': int_to_bytes_little(4, time)},
            {'unk1': hex_to_bytes(unk1)},
            {'username': str_to_bytes(username, 11)},
            {'unk2': hex_to_bytes(unk2)}
        ]
        return packet
