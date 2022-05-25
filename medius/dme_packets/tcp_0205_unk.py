from collections import deque
from utils.utils import *
import os

class tcp_0205_unk:
    def __init__(self, unk1="00000000000000000001FFFF81FF0000000000000000000000000000000000000000000000000000000000000000000040812200000000000087220000000000010000000000000003000000000000000000000000000000CC634800000000004083300000000000"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x05'
        self.unk1 = unk1

    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for i in range(104)])
        return tcp_0205_unk(unk1=unk1)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1}"
