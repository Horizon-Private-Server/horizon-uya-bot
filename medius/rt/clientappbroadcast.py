from utils.utils import *

from medius.dme_serializer import dme_serialize

class ClientAppBroadcastSerializer:
    data_dict = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'packets', 'n_bytes': None, 'cast': dme_serialize}
    ]

    def serialize(self, data: bytes):
        return serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, data: bytes):
        packet = [
            {'name': __name__},
            {'rtid': b'\x02'},
            {'data': data}
        ]
        return packet
