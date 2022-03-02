from collections import deque
from utils.utils import *
import os

class udp_020E_shot_fired:
    def __init__(self, weapon_type:str=None,
                           time:int=None,
                           moby_id:int=None,
                           unk2:int=None,
                           unk3:int=None,
                           unk4:int=None,
                           unk5:int=None,
                           unk6:int=None,
                           unk7:int=None
                        ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0E'
        self.weapon_type = weapon_type
        self.time = time
        self.moby_id = moby_id
        self.unk2 = unk2
        self.unk3 = unk3
        self.unk4 = unk4
        self.unk5 = unk5
        self.unk6 = unk6
        self.unk7 = unk7

    @classmethod
    def serialize(self, data: deque):
        weapon_type = ''.join([data.popleft() for i in range(4)])
        time = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        moby_id = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        if moby_id == 4294967295:
            moby_id = -1
        # unk2 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        # unk3 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        # unk4 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        # unk5 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        # unk6 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        # unk7 = hex_to_int_little(''.join([data.popleft() for i in range(4)]))

        unk2 = (''.join([data.popleft() for i in range(4)]))
        unk3 = (''.join([data.popleft() for i in range(4)]))
        unk4 = (''.join([data.popleft() for i in range(4)]))
        unk5 = (''.join([data.popleft() for i in range(4)]))
        unk6 = (''.join([data.popleft() for i in range(4)]))
        unk7 = (''.join([data.popleft() for i in range(4)]))

        return udp_020E_shot_fired(weapon_type, time, moby_id, unk2, unk3, unk4, unk5, unk6, unk7)

    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.weapon_type) + \
            int_to_bytes_little(4, self.time) + \
            int_to_bytes_little(4, self.moby_id if self.moby_id != -1 else 4294967295) + \
            int_to_bytes_little(4, self.unk2) + \
            int_to_bytes_little(4, self.unk3) + \
            int_to_bytes_little(4, self.unk4) + \
            int_to_bytes_little(4, self.unk5) + \
            int_to_bytes_little(4, self.unk6) + \
            int_to_bytes_little(4, self.unk7)

    def __str__(self):
        return f"{self.name}; weapon_type:{self.weapon_type} time:{self.time} moby_id:{self.moby_id} " + \
                f"unk2:{self.unk2} unk3:{self.unk3} unk4:{self.unk4} unk5:{self.unk5} unk6:{self.unk6} " + \
                f"unk7:{self.unk7}"
