from collections import deque
from butils.utils import *
import os

subtype_map = {
    '05': 'host_initial_handshake',
    '03': 'player_initial_handshake',
    '04': 'handshake'
}

class tcp_0016_player_connect_handshake:
    def __init__(self, subtype:str=None, src_player:int=None, unk1:str=None, unk2:str='00000000000000'):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x16'
        self.subtype = subtype
        self.src_player = src_player
        self.unk1 = unk1
        self.unk2 = unk2

    @classmethod
    def serialize(self, data: deque):
        subtype = subtype_map[data.popleft()]
        src_player = hex_to_int_little(data.popleft())
        unk1 = ''.join([data.popleft() for _ in range(7)])
        unk2 = ''.join([data.popleft() for _ in range(7)])
        return tcp_0016_player_connect_handshake(subtype, src_player, unk1, unk2)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
            int_to_bytes_little(1, self.src_player) + \
            hex_to_bytes(self.unk1) + \
            hex_to_bytes(self.unk2)

    def __str__(self):
        return f"{self.name}; subtype:{self.subtype} src_player:{self.src_player} unk1:{self.unk1} unk2:{self.unk2}"



# class tcp_0016_player_connect_handshake:
#     def __init__(self, data:str):
#         self.name = os.path.basename(__file__).strip(".py")
#         self.id = b'\x00\x16'
#         self.data = data # 16 length
#
#     @classmethod
#     def serialize(self, data: deque):
#         d = ''.join([data.popleft() for _ in range(16)])
#         return tcp_0016_player_connect_handshake(d)
#
#     def to_bytes(self):
#         return self.id + \
#             hex_to_bytes(self.data)
#
#     def __str__(self):
#         return f"{self.name}; data:{self.data}"
