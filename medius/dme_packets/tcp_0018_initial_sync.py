from collections import deque
from utils.utils import *
import os

class tcp_0018_initial_sync:
    def __init__(self, unk1:str="02000000",
                       src:int=None,
                       unk2:str='000000C0000264',
                       time:int=1100,
                       unk3:str='000000000000',
                       time2:int=700,
                       unk4:str='000001000000'
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x18'
        self.unk1 = unk1
        self.src = src
        self.unk2 = unk2
        self.time = time
        self.unk3 = unk3
        self.time2 = time2
        self.unk4 = unk4

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for _ in range(4)])
        src = hex_to_int_little(data.popleft())
        unk2 = ''.join([data.popleft() for _ in range(7)])
        time = hex_to_int_little(data.popleft() + data.popleft())
        unk3 = ''.join([data.popleft() for _ in range(6)]) #
        time2 = hex_to_int_little(data.popleft() + data.popleft())
        unk4 = ''.join([data.popleft() for _ in range(6)]) #

        return tcp_0018_initial_sync(unk1,src,unk2,time,unk3,time2,unk4)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1) + \
            int_to_bytes_little(4, self.src) + \
            hex_to_bytes(self.unk2) + \
            int_to_bytes_little(2, self.time) + \
            hex_to_bytes(self.unk3) + \
            int_to_bytes_little(2, self.time2) + \
            hex_to_bytes(self.unk4)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} src:{self.src} unk2:{self.unk2} time:{self.time} unk3:{self.unk3} time2:{self.time2} unk4:{self.unk4}"
