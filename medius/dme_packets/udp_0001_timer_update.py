from collections import deque
from butils.utils import *
import os

class udp_0001_timer_update:
    def __init__(self, time:int=0,
                       unk1:str="0300FFFF"
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x01'
        self.time = time
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        # Length = 32
        time = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

        unk1 = ''.join([data.popleft() for i in range(4)])

        return udp_0001_timer_update(time=time, unk1=unk1)


    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(4, self.time) + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; time:{self.time} unk1:{self.unk1}"
