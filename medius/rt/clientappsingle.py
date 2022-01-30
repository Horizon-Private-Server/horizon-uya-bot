from utils.utils import *

from medius.dme_serializer import dme_serialize

class ClientAppSingleSerializer:
    data_dict = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'src_player', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'buf', 'n_bytes': 1, 'cast': None},
        {'name': 'packets', 'n_bytes': None, 'cast': dme_serialize}
    ]

    def serialize(self, data: bytes):
        return serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, dst_player, data: bytes):
        packet = [
            {'name': __name__},
            {'rtid': b'\x03'},
            {'dst_player': int_to_bytes_little(2, dst_player)},
            {'data': data}
        ]
        return packet
