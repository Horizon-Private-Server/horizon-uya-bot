from collections import deque
from utils.utils import *
import os

class tcp_0010_initial_sync:
    def __init__(self, type:int=2, src:int=None, key:str="C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE"):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x10'
        self.type = type
        self.src = src
        self.key = key

    @classmethod
    def serialize(self, data: deque):
        type = hex_to_int_little(data.popleft())
        src = hex_to_int_little(data.popleft())
        key = ''.join([data.popleft() for _ in range(70)])

        return tcp_0010_initial_sync(type, src, key)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(1, self.type) + \
            int_to_bytes_little(1, self.src) + \
            hex_to_bytes(self.key)

    def __str__(self):
        return f"{self.name}; type:{self.type} src:{self.src} key:{self.key}"
