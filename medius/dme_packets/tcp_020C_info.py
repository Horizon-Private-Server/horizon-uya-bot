from collections import deque
from butils.utils import *
import os

from constants.constants import WEAPON_MAP

flag_drop_map = {
    '0100': 'p0_capture',
    '0101': 'p1_capture',
    '0102': 'p2_capture',
    '0103': 'p3_capture',
    '0104': 'p4_capture',
    '0105': 'p5_capture',
    '0106': 'p6_capture',
    '0107': 'p7_capture',
    '00FF': 'flag_return',
}


subtype_map = {
    '10401F00': '?_crate_destroyed',
    '41401F00': 'weapon_pickup',
    '41441F00': 'weapon_pickup_unk?_p1',
    '00401F00': 'crate_destroyed',
    '02401F00': 'crate_respawn',
    '02441F00': 'crate_respawn_p1?',
    '00000000': 'crate_destroyed_and_pickup',
    '10000000': '?_crate_destroyed_and_pickup',

    '02411F00': 'p0_flag_drop',
    '02451F00': 'p1_flag_drop',
    '02491F00': 'p2_flag_drop',
    '024D1F00': 'p3_flag_drop',
    '02511F00': 'p4_flag_drop',
    '02551F00': 'p5_flag_drop',
    '02591F00': 'p6_flag_drop',
    '025D1F00': 'p7_flag_drop',

    '61000000': 'p0_confirm',
    '61040000': 'p1_confirm',
    '61080000': 'p2_confirm',
    '610C0000': 'p3_confirm',
    '61100000': 'p4_confirm',
    '61140000': 'p5_confirm',
    '61180000': 'p6_confirm',
    '611C0000': 'p7_confirm',

    '73000000': 'p0_req_confirmation',
    '73040000': 'p1_req_confirmation',
    '73080000': 'p2_req_confirmation',
    '730C0000': 'p3_req_confirmation',
    '73100000': 'p4_req_confirmation',
    '73140000': 'p5_req_confirmation',
    '73180000': 'p6_req_confirmation',
    '731C0000': 'p7_req_confirmation',

    '40401F00': 'p0_object_update',
    '40441F00': 'p1_object_update',
    '40481F00': 'p2_object_update',
    '404C1F00': 'p3_object_update',
    '40501F00': 'p4_object_update',
    '40541F00': 'p5_object_update',
    '40581F00': 'p6_object_update',
    '405C1F00': 'p7_object_update',

    '21000000': 'p0_flag_update',
    '21040000': 'p1_flag_update',
    '21080000': 'p2_flag_update',
    '210C0000': 'p3_flag_update',
    '21100000': 'p4_flag_update',
    '21140000': 'p5_flag_update',
    '21180000': 'p6_flag_update',
    '211C0000': 'p7_flag_update',

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
        elif 'flag_update' in subtype:
            data_dict['flag_update_type'] =  flag_drop_map[''.join([data.popleft() for i in range(2)])]
        elif 'flag_drop' in subtype:
            data_dict['flag_drop_unk'] =  ''.join([data.popleft() for i in range(16)])
        elif subtype in ['p0_confirm', 'p1_confirm', 'p2_confirm', 'p3_confirm', 'p4_confirm', 'p5_confirm', 'p6_confirm', 'p7_confirm']:
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['unk'] = ''.join([data.popleft() for i in range(2)])
        elif subtype in ['p0_req_confirmation', 'p1_req_confirmation', 'p2_req_confirmation', 'p3_req_confirmation', 'p4_req_confirmation', 'p5_req_confirmation', 'p6_req_confirmation', 'p7_req_confirmation']:
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['buf'] = ''.join([data.popleft() for i in range(1)])
            data_dict['unk'] = ''.join([data.popleft() for i in range(2)])
        elif subtype == 'crate_respawn_p1?':
            pass
        elif subtype == 'weapon_pickup_unk?_p1':
            data_dict['unk'] =  ''.join([data.popleft() for i in range(4)])

        return tcp_020C_info(subtype, timestamp, object_id, data_dict)

    def to_bytes(self):
        if self.subtype in ['p0_confirm', 'p1_confirm', 'p2_confirm', 'p3_confirm', 'p4_confirm', 'p5_confirm', 'p6_confirm', 'p7_confirm']:
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_id) + \
                hex_to_bytes(self.data['object_id']) + \
                hex_to_bytes(self.data['unk'])
        elif self.subtype in ['p0_req_confirmation', 'p1_req_confirmation', 'p2_req_confirmation', 'p3_req_confirmation', 'p4_req_confirmation', 'p5_req_confirmation', 'p6_req_confirmation', 'p7_req_confirmation']:
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_id) + \
                hex_to_bytes(self.data['object_id']) + \
                hex_to_bytes('00') + \
                hex_to_bytes(self.data['unk'])
        elif 'flag_drop' in self.subtype:
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
