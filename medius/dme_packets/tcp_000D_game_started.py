from collections import deque
import os
from butils.utils import *

class tcp_000D_game_started:
    def __init__(self, unk1:str='0000'):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x0D'
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for _ in range(2)])
        return tcp_000D_game_started(unk1)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1}"
