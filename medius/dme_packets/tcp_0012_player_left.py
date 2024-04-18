from collections import deque
import os
from butils.utils import *

class tcp_0012_player_left:
    def __init__(self, player_id:str='00'):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x12'
        self.player_id = player_id

    @classmethod
    def serialize(self, data: deque):
        player_id = data.popleft()
        return tcp_0012_player_left(player_id)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.player_id)

    def __str__(self):
        return f"{self.name}; unk1:{self.player_id}"
