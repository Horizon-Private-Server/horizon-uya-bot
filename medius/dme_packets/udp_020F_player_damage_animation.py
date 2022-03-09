from collections import deque
from utils.utils import *
import os

class udp_020F_player_damage_animation:
    def __init__(self, unk1:str="031DE53CD28A413DC074D63A22010300"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0F'
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for i in range(16)])
        return udp_020F_player_damage_animation(unk1=unk1)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1}"
