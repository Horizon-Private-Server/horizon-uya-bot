from collections import deque
from butils.utils import *
import os

class udp_020F_player_damage_animation:
    def __init__(self, unk1:str="031DE53CD28A413DC074D63A22", src_player:int=None, unk2="0300"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0F'
        self.unk1 = unk1
        self.src_player = src_player
        self.unk2 = unk2

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for i in range(13)])
        src_player = hex_to_int_little(data.popleft())
        unk2 = ''.join([data.popleft() for i in range(2)])
        return udp_020F_player_damage_animation(unk1=unk1, src_player=src_player, unk2=unk2)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1) + \
            int_to_bytes_little(1, self.src_player) + \
            hex_to_bytes(self.unk2)


    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} src_player:{self.src_player} unk2:{self.unk2}"
