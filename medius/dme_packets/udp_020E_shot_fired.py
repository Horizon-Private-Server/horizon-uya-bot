from collections import deque
from utils.utils import *
import os
from constants.constants import WEAPON_MAP
'''
P0 moby: 1
P1 moby: 268435457
P2 moby: 536870913

P0 n60 :
P0 bltz:
P0 flux:
P0 rckt:
P0 grav:
P0 mine:
P0 lava:
P0 mrph:
P1 hypr:

P1 flux: 4108
P2 flux: 4208
'''

object_id_map = {
    1: 0,
    268435457: 1,
    536870913: 2,
    805306369: 3,
    1610612737: 4,
    1342177281: 5,
    1073741825: 6,
    1879048193: 7,
    4294967295: -1
}

WEAPON_MAP_SRC = {
    'n60': '0{}08',
    'blitz': '0{}08',
    'flux': '4{}08',
    'rocket': '0{}08',
    'grav': '0{}08',
    'mine': '0{}08',
    'lava': '0{}08',
    'morph': '0{}01',
    'hyper': '0{}02',
}

class udp_020E_shot_fired:
    def __init__(self, weapon:str=None,
                           src_player:int=None,
                           time:int=None,
                           object_id:int=None,
                           unk2:int=0,
                           unk3:int=0,
                           unk4:int=0,
                           unk5:int=0,
                           unk6:int=0,
                           unk7:int=0
                        ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0E'
        self.weapon = weapon
        self.src_player = src_player
        self.time = time
        self.object_id = object_id
        self.unk2 = unk2
        self.unk3 = unk3
        self.unk4 = unk4
        self.unk5 = unk5
        self.unk6 = unk6
        self.unk7 = unk7

    @classmethod
    def serialize(self, data: deque):
        weapon = WEAPON_MAP[data.popleft()]
        data.popleft()
        temp = ''.join([data.popleft() for i in range(2)])
        src_player = int(temp[1])

        time = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        moby_id = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

        if moby_id not in object_id_map.keys():
            object_id = moby_id
        else:
            object_id = object_id_map[moby_id]

        unk2 = (''.join([data.popleft() for i in range(4)]))
        unk3 = (''.join([data.popleft() for i in range(4)]))
        unk4 = (''.join([data.popleft() for i in range(4)]))
        unk5 = (''.join([data.popleft() for i in range(4)]))
        unk6 = (''.join([data.popleft() for i in range(4)]))
        unk7 = (''.join([data.popleft() for i in range(4)]))

        return udp_020E_shot_fired(weapon, src_player, time, object_id, unk2, unk3, unk4, unk5, unk6, unk7)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes({v: k for k, v in WEAPON_MAP.items()}[self.weapon]) + \
            hex_to_bytes("00") + \
            hex_to_bytes(WEAPON_MAP_SRC[self.weapon].format(self.src_player)) + \
            int_to_bytes_little(4, self.time) + \
            int_to_bytes_little(4, {v: k for k, v in object_id_map.items()}[self.object_id]) + \
            int_to_bytes_little(4, self.unk2) + \
            int_to_bytes_little(4, self.unk3) + \
            int_to_bytes_little(4, self.unk4) + \
            int_to_bytes_little(4, self.unk5) + \
            int_to_bytes_little(4, self.unk6) + \
            int_to_bytes_little(4, self.unk7)

    def __str__(self):
        return f"{self.name}; weapon:{self.weapon} src_player:{self.src_player} time:{self.time} object_id:{self.object_id} " + \
                f"unk2:{self.unk2} unk3:{self.unk3} unk4:{self.unk4} unk5:{self.unk5} unk6:{self.unk6} " + \
                f"unk7:{self.unk7}"
