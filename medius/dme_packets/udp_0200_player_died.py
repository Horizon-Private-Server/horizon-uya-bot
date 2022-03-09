from collections import deque
from utils.utils import *
import os

class udp_0200_player_died:
    def __init__(self, src_player:int=None, unk1:str="396D0267BCA8433B0CBD4300E0074200A08238008075B800B906C0"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x00'
        self.src_player = src_player
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        src_player = int(data.popleft(), 16)
        unk1 = ''.join([data.popleft() for i in range(27)])
        return udp_0200_player_died(src_player=src_player, unk1=unk1)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(1, self.src_player) + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; src_player:{self.src_player} unk1:{self.unk1}"
