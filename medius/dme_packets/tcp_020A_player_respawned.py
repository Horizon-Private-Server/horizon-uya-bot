from collections import deque
from butils.utils import *
import os

class tcp_020A_player_respawned:
    def __init__(self, src_player:int=None, data={}):
        # 000138CCA1A143C5ADB043CC2C08420000000000000000E964823F00000100
        # old: 00012DD7D3FD43831C5A4466CEE7420000000000000000B2B3BA3F00000100
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0A'
        self.src_player = src_player
        self.data = data


    @classmethod
    def serialize(self, data: deque):
        src_player = hex_to_int_little(data.popleft())
        data.popleft() # '00'

        d = {}
        d['unk0'] = ''.join([data.popleft() for i in range(3)])
        d['offset_x'] = hex_to_int_little(data.popleft()) / 255 
        d['local_x'] = short_bytes_to_int(data.popleft(), data.popleft())
        d['unk1'] = ''.join([data.popleft() for i in range(1)])
        d['offset_y'] = hex_to_int_little(data.popleft()) / 255 
        d['local_y'] = short_bytes_to_int(data.popleft(), data.popleft())
        d['unk2'] = ''.join([data.popleft() for i in range(1)])
        d['offset_z'] = hex_to_int_little(data.popleft()) / 255 
        d['local_z'] = short_bytes_to_int(data.popleft(), data.popleft())
        d['unk3'] = ''.join([data.popleft() for i in range(16)])

        return tcp_020A_player_respawned(src_player=src_player, data=d)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(1, self.src_player) + \
            hex_to_bytes("00") + \
            hex_to_bytes("000000") + \
            int_to_bytes_little(1, int((self.data['local_x'] - int(self.data['local_x']))*255)) + \
            int_to_bytes_little(2, int(self.data['local_x'])) + \
            hex_to_bytes("00") + \
            int_to_bytes_little(1, int((self.data['local_y'] - int(self.data['local_y']))*255)) + \
            int_to_bytes_little(2, int(self.data['local_y'])) + \
            hex_to_bytes("00") + \
            int_to_bytes_little(1, int((self.data['local_z'] - int(self.data['local_z']))*255)) + \
            int_to_bytes_little(2, int(self.data['local_z'])) + \
            hex_to_bytes("00000000000000000000000000000100")

# unk3=00000000000000000000000000000100

    def __str__(self):
        return f"{self.name}; src_player:{self.src_player} data:{self.data}"
