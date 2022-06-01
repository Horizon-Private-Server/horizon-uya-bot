from butils.utils import *

class ServerConnectCompleteSerializer:
    data_dict = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little}
    ]

    def serialize(self, data: bytes):
        return serialize(data, self.data_dict, __name__)

    @classmethod
    def build(self, player_count=1):
        packet = [
            {'name': __name__},
            {'rtid': 0x1a},
            {'connect_complete': int_to_bytes_little(2, player_count)}
        ]
        return packet

class ServerConnectCompleteHandler:
    def process(self, serialized, monolith, con):
        raise Exception('Unimplemented Handler: ServerConnectCompleteHandler')
