'''
0204003901030000000001000000 butchered
0204003901030100000001000000 liquidated
0204003901030200000001000000 extirpated
0204003901030300000001000000 exterminated
0204003901030400000001000000 mousetrapped
0204003901030500000001000000 kervorked
0204003901030600000001000000 flatlined
0204003901030700000001000000 abolished
0204003901030800000001000000 eviscerated
0204003901030900000001000000 cremated
0204003901030A00000001000000 dismembered
0204003901030B00000001000000 euthanized
0204003901030C00000001000000 tomahawked
0204003901030D00000001000000 expunged
0204003901030E00000001000000 devastated
0204003901030F00000001000000 smoked

0204003901030F00000001000000

0204003901030700000001000000 -- flux
0204003901050700000001000000 -- grav


1 kills 0
0204
01 -- killer
39 -- unk1
00 -- killed
03 -- weapon
0F -- kill_msg
00000001000000 -- unk3
'''
from collections import deque
from utils.utils import *
import os
from constants.constants import WEAPON_MAP, KILL_MSG_MAP

class tcp_0204_player_killed:
    def __init__(self, killer_id:int=None,
                           unk1:str='39',
                           killed_id:int=None,
                           weapon:str=None,
                           kill_msg:str=None,
                           unk2:str='00000001000000'
                        ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x04'
        self.killer_id = killer_id
        self.unk1 = unk1
        self.killed_id = killed_id
        self.weapon = weapon
        self.kill_msg = kill_msg
        self.unk2 = unk2

    @classmethod
    def serialize(self, data: deque):
        killer_id = hex_to_int_little(data.popleft())
        unk1 = data.popleft()
        killed_id = hex_to_int_little(data.popleft())
        weapon = WEAPON_MAP[data.popleft()]
        kill_msg = KILL_MSG_MAP[data.popleft()]
        unk2 = ''.join([data.popleft() for i in range(7)])
        return tcp_0204_player_killed(killer_id, unk1, killed_id, weapon, kill_msg, unk2)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(1, self.killer_id) + \
            hex_to_bytes(self.unk1) + \
            int_to_bytes_little(1, self.killed_id) + \
            hex_to_bytes({v: k for k, v in WEAPON_MAP.items()}[self.weapon]) + \
            hex_to_bytes({v: k for k, v in KILL_MSG_MAP.items()}[self.kill_msg]) + \
            hex_to_bytes(self.unk2)

    def __str__(self):
        return f"{self.name}; killer_id:{self.killer_id} unk1:{self.unk1} killed_id:{self.killed_id} " + \
                f"weapon:{self.weapon} kill_msg:{self.kill_msg} unk2:{self.unk2}"
