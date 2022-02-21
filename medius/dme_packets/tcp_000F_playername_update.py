from collections import deque
import os
from utils.utils import *

class tcp_000F_playername_update:
    def __init__(self, unk1:int=1, unk2:str="00000000000003000300000000001A000000", username:str=None, unk3:str="000300"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x0F'
        self.unk1 = unk1
        self.unk2 = unk2
        self.username = username
        self.unk3 = unk3

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for _ in range(4)])
        unk2 = ''.join([data.popleft() for _ in range(18)])
        username = hex_to_str(''.join([data.popleft() for _ in range(11)]))
        unk3 = ''.join([data.popleft() for _ in range(3)])
        return tcp_000F_playername_update(unk1, unk2, username, unk3)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(4, self.unk1) + \
            hex_to_bytes(self.unk2) + \
            str_to_bytes(self.username, 11) + \
            hex_to_bytes(self.unk3)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} unk2:{self.unk2} username:{self.username} unk3:{self.unk3}"
