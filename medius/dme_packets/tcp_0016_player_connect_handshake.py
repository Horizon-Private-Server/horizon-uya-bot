from collections import deque
from utils.utils import *
import os

class tcp_0016_player_connect_handshake:
    def __init__(self, data:str):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x16'
        self.data = data # 16 length

    @classmethod
    def serialize(self, data: deque):
        d = ''.join([data.popleft() for _ in range(16)])
        return tcp_0016_player_connect_handshake(d)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.data)

    def __str__(self):
        return f"{self.name}; data:{self.data}"
