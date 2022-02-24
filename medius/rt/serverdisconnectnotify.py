from utils.utils import *

from medius.dme_serializer import dme_serialize

class ServerDisconnectNotifySerializer:
    data_dict = [
        {'name': 'rtid', 'n_bytes': 1, 'cast': None},
        {'name': 'len', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'dme_player_id', 'n_bytes': 2, 'cast': bytes_to_int_little},
        {'name': 'ip', 'n_bytes': 16, 'cast': None}
    ]

    def serialize(self, data: bytes):
        return serialize(data, self.data_dict, __name__)
