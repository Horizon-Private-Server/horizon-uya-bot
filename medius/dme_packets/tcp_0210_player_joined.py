from utils.utils import *

'''
This packet is sent to others when they join the game.

This packet is received when first joining a game, and they send it to us
'''

class tcp_0210_player_joined:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'type', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'account_id', 'n_bytes': 4, 'cast': bytes_to_int_little},
        {'name': 'rank', 'n_bytes': 32, 'cast': None}, # C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF430000000000000000424242424242424242424242424200414242424242424242424242427E3200004242424200000000
        {'name': 'buf', 'n_bytes': 4, 'cast': None},
        {'name': 'skin1', 'n_bytes': 2, 'cast': None},
        {'name': 'skin2', 'n_bytes': 2, 'cast': None},

        {'name': 'username', 'n_bytes': 14, 'cast': bytes_to_str},
        {'name': 'buf2', 'n_bytes': 2, 'cast': None},
        {'name': 'username', 'n_bytes': 12, 'cast': bytes_to_str},
        {'name': 'buf3', 'n_bytes': 12, 'cast': None},
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, account_id, skin, username, rank, clantag = 'AAAA'):
        packet = [
            {'name': __name__},
            {'dme_id': b'\x02\x10'},
            {'type': int_to_bytes_little(4, 1)},
            {'account_id': int_to_bytes_little(4, account_id)},
            {'rank': hex_to_bytes(rank)},
            {'buf': hex_to_bytes('00000000')},
            {'skin1': int_to_bytes_little(2, skin)},
            {'skin2': int_to_bytes_little(2, skin)},
            {'username': str_to_bytes(username,14)},
            {'buf': hex_to_bytes('0034')},
            {'username': str_to_bytes(username,12)},
            {'buf': hex_to_bytes('7E320000')},
            {'clan_tag': str_to_bytes(clantag,4)},
            {'buf': hex_to_bytes('00000000')},
        ]

        return packet
