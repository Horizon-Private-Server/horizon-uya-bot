'''
0207
18000000
00000000
02000000
11000002
50AB1B00
11000002


0207
1C000000
01000000
01000000
03000012
30AE1B00
02000000
01000000

0207
20000000
01000000
01000000
0B000012
F4F73300
03000000
01000000
00000000


'''
from collections import deque
from butils.utils import *
import os

from constants.constants import TEAM_MAP, SKIN_MAP

class tcp_0207_defenses:
    def __init__(self, data
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x07'
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        d = {}
        d['byte_len'] = hex_to_int_little(''.join([data.popleft() for i in range(4)])) - 20
        d['src_player'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        d['unk_1'] = ''.join([data.popleft() for i in range(4)])
        d['unk_2'] = ''.join([data.popleft() for i in range(4)])
        d['time'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

        d['leftover'] = ''.join([data.popleft() for i in range(d['byte_len'])])

        return tcp_0207_defenses(d)

    def to_bytes(self):
        return self.id

    def __str__(self):
        return f"{self.name}; data:{self.data}"