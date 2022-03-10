from collections import deque
from utils.utils import *
import os

class tcp_020A_player_respawned:
    def __init__(self, src_player:int=None, unk1="000138CCA1A143C5ADB043CC2C08420000000000000000E964823F00000100"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0A'
        self.src_player = src_player
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        src_player = hex_to_int_little(data.popleft())
        unk1 = ''.join([data.popleft() for i in range(31)])
        return tcp_020A_player_respawned(src_player=src_player, unk1=unk1)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(1, self.src_player) + \
            hex_to_bytes(self.unk1)


    def __str__(self):
        return f"{self.name}; src_player:{self.src_player} unk1:{self.unk1}"
