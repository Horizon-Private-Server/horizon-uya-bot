from collections import deque
import os
from utils.utils import *

class tcp_0009_set_timer:
    def __init__(self, time:int=None, unk1:str='03000000001702000000'):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x09'
        self.time = time
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        time = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        unk1 = ''.join([data.popleft() for _ in range(10)])
        return tcp_0009_set_timer(time, unk1)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(4, self.time) + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; time:{self.time} unk1:{self.unk1}"
