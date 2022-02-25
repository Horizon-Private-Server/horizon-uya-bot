from utils.utils import *

from medius.dme_serializer import dmetcp_serialize, dmeudp_serialize

class ClientAppSingleSerializer:
    data_dict_tcp = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'src_player', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'buf', 'n_bytes': 1, 'cast': None},
        {'name': 'packets', 'n_bytes': None, 'cast': dmetcp_serialize}
    ]

    data_dict_udp = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'src_player', 'n_bytes': 1, 'cast': bytes_to_int_little},
        {'name': 'buf', 'n_bytes': 1, 'cast': None},
        {'name': 'packets', 'n_bytes': None, 'cast': dmeudp_serialize}
    ]

    def __init__(self, protocol):
        self.protocol = protocol

    def serialize(self, data: bytes):
        if self.protocol == 'tcp':
            serialized = serialize(data, self.data_dict_tcp, __name__)
        elif self.protocol == 'udp':
            serialized = serialize(data, self.data_dict_udp, __name__)
        serialized['protocol'] = self.protocol
        return serialized

    @classmethod
    def build(self, dst_player, data: bytes):
        packet = [
            {'name': __name__},
            {'rtid': b'\x03'},
            {'dst_player': int_to_bytes_little(2, dst_player)},
            {'data': data}
        ]
        return packet
