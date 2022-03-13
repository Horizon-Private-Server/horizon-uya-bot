from collections import deque
from utils.utils import *
import os

from constants.constants import WEAPON_MAP

subtype_map = {
    '10401F00': '?_crate_destroyed',
    '41401F00': 'weapon_pickup',
    '00401F00': 'crate_destroyed',
    '02401F00': 'crate_respawn',
    '00000000': 'crate_destroyed_and_pickup',
    '10000000': '?_crate_destroyed_and_pickup'
}


class tcp_020C_info:
    def __init__(self, subtype:str=None,
                       timestamp:int=None,
                       subtype_id:str=None,
                       data:dict=None
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0C'
        self.subtype = subtype
        self.timestamp = timestamp
        self.subtype_id = subtype_id
        self.data = data


    @classmethod
    def serialize(self, data: deque):
        print(''.join(list(data)))
        subtype = ''.join([data.popleft() for i in range(4)])
        subtype = subtype_map[subtype]
        timestamp = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        subtype_id = ''.join([data.popleft() for i in range(4)])

        data_dict = {}
        if subtype in ['?_crate_destroyed_and_pickup', '?_crate_destroyed']:
            data_dict['weapon_spawned'] = WEAPON_MAP[data.popleft()]
        if subtype == 'weapon_pickup':
            data_dict['weapon_pickup_unk'] =  ''.join([data.popleft() for i in range(4)])
        return tcp_020C_info(subtype, timestamp, subtype_id, data_dict)

    # def to_bytes(self):
    #     return self.id + \
    #         int_to_bytes_little(4, self.type) + \
    #         int_to_bytes_little(4, self.account_id) + \
    #         hex_to_bytes(self.rank) + \
    #         hex_to_bytes(self.unk1) + \
    #         hex_to_bytes({v: k for k, v in SKIN_MAP.items()}[self.skin1] + '00') + \
    #         hex_to_bytes({v: k for k, v in SKIN_MAP.items()}[self.skin2] + '00') + \
    #         str_to_bytes(self.username, 14) + \
    #         hex_to_bytes(self.unk2) + \
    #         str_to_bytes(self.username2, 12) + \
    #         hex_to_bytes(self.unk3) + \
    #         str_to_bytes(self.clan_tag, 4) + \
    #         hex_to_bytes(self.unk4)

    def __str__(self):
        return f"{self.name}; subtype:{self.subtype} " + \
                f"timestamp:{self.timestamp} subtype_id:{self.subtype_id} data:{self.data}"
