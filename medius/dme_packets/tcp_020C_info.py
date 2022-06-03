from collections import deque
from butils.utils import *
import os

from constants.constants import WEAPON_MAP

'''
cc:
red flag: 131000F7
blue flag: 141000F7

dox:
red flag: 0E1000F7
blue flag: 0F1000F7

marc:
red flag: 131000F7
blue flag: 141000F7

sewers:
red flag: 121000F7
blue flag: 131000F7

bwc
-- no nodes, bd on
red flag: 3D1000F7
blue flag:
-- no nodes, bd off
red flag:
blue flag: 

'''
subtype_map = {
    '10401F00': '?_crate_destroyed',
    '41401F00': 'weapon_pickup',
    '41441F00': 'weapon_pickup_unk?_p1',
    '00401F00': 'crate_destroyed',
    '02401F00': 'crate_respawn',
    '02441F00': 'crate_respawn_p1?',
    '00000000': 'crate_destroyed_and_pickup',
    '10000000': '?_crate_destroyed_and_pickup',
    '21000000': 'flag_update',
    '02411F00': 'flag_drop',
    '61000000': 'p0_confirm',
    '61040000': 'p1_confirm',
    '73000000': 'p0_req_confirmation',
    '73040000': 'p1_req_confirmation',

    '40401F00': 'p0_object_update',
    '40441F00': 'p1_object_update',
}

'''
020C
40441F00
17680C00
141000F7
01000000
'''

class tcp_020C_info:
    def __init__(self, subtype:str=None,
                       timestamp:int=None,
                       object_id:str=None,
                       data:dict=None
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0C'
        self.subtype = subtype
        self.timestamp = timestamp
        self.object_id = object_id
        self.data = data


    @classmethod
    def serialize(self, data: deque):
        #print(''.join(list(data)))
        subtype = ''.join([data.popleft() for i in range(4)])
        subtype = subtype_map[subtype]
        timestamp = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        object_id = ''.join([data.popleft() for i in range(4)])

        data_dict = {}

        if subtype in ['?_crate_destroyed_and_pickup', '?_crate_destroyed']:
            data_dict['weapon_spawned'] = WEAPON_MAP[data.popleft()]
        elif subtype == 'weapon_pickup':
            data_dict['weapon_pickup_unk'] =  ''.join([data.popleft() for i in range(4)])
        elif 'object_update' in subtype:
            data_dict['object_update_unk'] =  ''.join([data.popleft() for i in range(4)])
        elif subtype == 'flag_update':
            data_dict['flag_update_type'] =  ''.join([data.popleft() for i in range(2)])
        elif subtype == 'flag_drop':
            data_dict['flag_drop_unk'] =  ''.join([data.popleft() for i in range(16)])
        elif subtype in ['p0_confirm', 'p1_confirm']:
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['unk'] = ''.join([data.popleft() for i in range(2)])
        elif subtype in ['p0_req_confirmation', 'p1_req_confirmation']:
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['buf'] = ''.join([data.popleft() for i in range(1)])
            data_dict['unk'] = ''.join([data.popleft() for i in range(2)])
        elif subtype == 'crate_respawn_p1?':
            pass
        elif subtype == 'weapon_pickup_unk?_p1':
            data_dict['unk'] =  ''.join([data.popleft() for i in range(4)])




        return tcp_020C_info(subtype, timestamp, object_id, data_dict)

    def to_bytes(self):
        if self.subtype == 'p1_confirm':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_id) + \
                hex_to_bytes(self.data['object_id']) + \
                hex_to_bytes(self.data['unk'])
        elif self.subtype == 'p1_req_confirmation':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_id) + \
                hex_to_bytes(self.data['object_id']) + \
                hex_to_bytes('00') + \
                hex_to_bytes(self.data['unk'])

    def __str__(self):
        return f"{self.name}; subtype:{self.subtype} " + \
                f"timestamp:{self.timestamp} object_id:{self.object_id} data:{self.data}"
