from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tcp_0010_initial_sync:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 1, 'cast': bytes_to_int_little}, # 00
        {'name': 'src_player?', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'key', 'n_bytes': 70, 'cast': None}, # C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, src_player_id):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x00\x10'},
            {'unk1': hex_to_bytes('02')},
            {'src_player?': int_to_bytes_little(1, src_player_id)},
            {'unk2': hex_to_bytes('C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE')}
        ]
        return packet
