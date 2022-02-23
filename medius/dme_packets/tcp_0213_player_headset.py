from collections import deque
import os
from utils.utils import *

class tcp_0213_player_headset:
    def __init__(self, unk1:str='00000000'):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x13'
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for _ in range(4)])
        return tcp_0213_player_headset(unk1)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1}"
