from utils.utils import *


class tcp_0009_unk:
    data_dict = [
        {'name': 'dme_id', 'n_bytes': 2, 'cast': None},
        {'name': 'unk1', 'n_bytes': 14, 'cast': bytes_to_int_little}, # CC6F070003000000001702000000
    ]

    def serialize(self, data: bytearray):
        return dme_serialize(data, self.data_dict, __name__)

    # @classmethod
    # def build(self, player_id, message_type=2):
    #     packet = [
    #         {'name': __name__},
    #         {'dme_id': b'\x02\x10'},
    #         {'src_player_id?': int_to_bytes_little(4, player_id)},
    #         {'message_type': int_to_bytes_little(4, message_type)},
    #         {'unk': hex_to_bytes('0C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF430000000000000000424242424242424242424242424200414242424242424242424242427E3200004242424200000000')}
    #     ]
    #     return packet
