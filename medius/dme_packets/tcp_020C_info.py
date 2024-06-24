from collections import deque
from butils.utils import *
import os

from constants.constants import WEAPON_MAP


player_object_pickup_map = {
    0: 0,
    16: 1,
    32: 2,
    48: 3,
    64: 4,
    80: 5,
    96: 6,
    112: 7
}


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

    '02411F00': 'p0_flag_drop',
    '02451F00': 'p1_flag_drop',
    '02491F00': 'p2_flag_drop',
    '024D1F00': 'p3_flag_drop',
    '02511F00': 'p4_flag_drop',
    '02551F00': 'p5_flag_drop',
    '02591F00': 'p6_flag_drop',
    '025D1F00': 'p7_flag_drop',

    '61000000': 'p0_assign_to',
    '61040000': 'p1_assign_to',
    '61080000': 'p2_assign_to',
    '610C0000': 'p3_assign_to',
    '61100000': 'p4_assign_to',
    '61140000': 'p5_assign_to',
    '61180000': 'p6_assign_to',
    '611C0000': 'p7_assign_to',

    '73000000': 'p0_change_owner_req',
    '73040000': 'p1_change_owner_req',
    '73080000': 'p2_change_owner_req',
    '730C0000': 'p3_change_owner_req',
    '73100000': 'p4_change_owner_req',
    '73140000': 'p5_change_owner_req',
    '73180000': 'p6_change_owner_req',
    '731C0000': 'p7_change_owner_req',

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

    '00401F00': 'p0_crate_destroyed',
    '00441F00': 'p1_crate_destroyed',
    '00481F00': 'p2_crate_destroyed',
    '004C1F00': 'p3_crate_destroyed',
    '00501F00': 'p4_crate_destroyed',
    '00541F00': 'p5_crate_destroyed',
    '00581F00': 'p6_crate_destroyed',
    '005C1F00': 'p7_crate_destroyed',

    '10401F00': 'p0_?_crate_destroyed',
    '10441F00': 'p1_?_crate_destroyed',
    '10481F00': 'p2_?_crate_destroyed',
    '104C1F00': 'p3_?_crate_destroyed',
    '10501F00': 'p4_?_crate_destroyed',
    '10541F00': 'p5_?_crate_destroyed',
    '10581F00': 'p6_?_crate_destroyed',
    '105C1F00': 'p7_?_crate_destroyed',

    '02401F00': 'p0_crate_respawn',
    '02441F00': 'p1_crate_respawn',
    '02481F00': 'p2_crate_respawn',
    '024C1F00': 'p3_crate_respawn',
    '02501F00': 'p4_crate_respawn',
    '02541F00': 'p5_crate_respawn',
    '02581F00': 'p6_crate_respawn',
    '025C1F00': 'p7_crate_respawn',

    '41401F00': 'p0_object_pickup',
    '41441F00': 'p1_object_pickup',
    '41481F00': 'p2_object_pickup',
    '414C1F00': 'p3_object_pickup',
    '41501F00': 'p4_object_pickup',
    '41541F00': 'p5_object_pickup',
    '41581F00': 'p6_object_pickup',
    '415C1F00': 'p7_object_pickup',

    '62000000': 'p0_object_update_req',
    '62040000': 'p1_object_update_req',
    '62080000': 'p2_object_update_req',
    '620C0000': 'p3_object_update_req',
    '62100000': 'p4_object_update_req',
    '62140000': 'p5_object_update_req',
    '62180000': 'p6_object_update_req',
    '621C0000': 'p7_object_update_req',

    '00000000': 'p0_crate_destroyed_and_pickup',
    '00040000': 'p1_crate_destroyed_and_pickup',
    '00080000': 'p2_crate_destroyed_and_pickup',
    '000C0000': 'p3_crate_destroyed_and_pickup',
    '00100000': 'p4_crate_destroyed_and_pickup',
    '00140000': 'p5_crate_destroyed_and_pickup',
    '00180000': 'p6_crate_destroyed_and_pickup',
    '001C0000': 'p7_crate_destroyed_and_pickup',

    '10000000': 'p0_?_crate_destroyed_and_pickup',
    '10040000': 'p1_?_crate_destroyed_and_pickup',
    '10080000': 'p2_?_crate_destroyed_and_pickup',
    '100C0000': 'p3_?_crate_destroyed_and_pickup',
    '10100000': 'p4_?_crate_destroyed_and_pickup',
    '10140000': 'p5_?_crate_destroyed_and_pickup',
    '10180000': 'p6_?_crate_destroyed_and_pickup',
    '101C0000': 'p7_?_crate_destroyed_and_pickup',


}

'''
020C
10040000
56430701
081000F7
05
'''



class tcp_020C_info:
    def __init__(self, subtype:str=None,
                       timestamp:int=None,
                       object_type:str=None,
                       data:dict=None
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x0C'
        self.subtype = subtype
        self.timestamp = timestamp
        self.object_type = object_type
        self.data = data


    @classmethod
    def serialize(self, data: deque):
        #print(''.join(list(data)))

        #print(dequeue_to_str(data))

        subtype = ''.join([data.popleft() for i in range(4)])
        subtype = subtype_map[subtype]
        timestamp = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        object_type = ''.join([data.popleft() for i in range(4)])

        data_dict = {}

        if subtype[2:] in ['_?_crate_destroyed', '_?_crate_destroyed_and_pickup']:
            data_dict['weapon_spawned'] = WEAPON_MAP[data.popleft()]
        elif subtype[2:] == '_object_update' in subtype:
            data_dict['object_update_unk'] =  ''.join([data.popleft() for i in range(4)])
        elif subtype[2:] == '_flag_update':
            data_dict['flag_update_type'] =  flag_drop_map[''.join([data.popleft() for i in range(2)])]
        elif 'flag_drop' in subtype:
            data_dict['flag_drop_unk'] =  ''.join([data.popleft() for i in range(16)])
        elif subtype[2:] == '_assign_to':
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['counter'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
            data_dict['master'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
        elif subtype[2:] == '_change_owner_req':
            data_dict['object_id'] = ''.join([data.popleft() for i in range(4)])
            data_dict['new_owner'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
            data_dict['counter'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
            data_dict['master'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
        elif subtype[2:] == '_crate_respawn':
            pass
        # The unk is 010000 for weapon boxes and health
        elif subtype[2:] == '_object_pickup':
            data_dict['unk'] =  ''.join([data.popleft() for i in range(3)])
            #data_dict['player_who_picked_up'] =  hex_to_int_little(data.popleft())
            data_dict['player_who_picked_up'] =  player_object_pickup_map[hex_to_int_little(data.popleft())]
        elif subtype[2:] == '_object_update_req':
            data_dict['object_id'] =  ''.join([data.popleft() for i in range(4)])
            data_dict['counter'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))
            data_dict['master'] = hex_to_int_little(''.join([data.popleft() for i in range(1)]))

        return tcp_020C_info(subtype, timestamp, object_type, data_dict)

    def to_bytes(self):
        if self.subtype[2:] == '_assign_to':
            # object type is always 001000F7
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes("001000F7") + \
                hex_to_bytes(self.data['object_id']) + \
                int_to_bytes_little(1, self.data['counter']) + \
                int_to_bytes_little(1, self.data['master'])
        elif self.subtype[2:] == '_change_owner_req':
            # object type is always 001000F7
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes("001000F7") + \
                hex_to_bytes(self.data['object_id']) + \
                int_to_bytes_little(1, self.data['new_owner']) + \
                int_to_bytes_little(1, self.data['counter']) + \
                int_to_bytes_little(1, self.data['master'])
        elif self.subtype[2:] == '_object_pickup':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_type) + \
                hex_to_bytes("010000") + \
                int_to_bytes_little(1, {v: k for k, v in player_object_pickup_map.items()}[self.data['player_who_picked_up']])
        elif self.subtype[2:] == '_flag_drop':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_type) + \
                hex_to_bytes(self.data['flag_drop_unk'])
        elif self.subtype[2:] == '_crate_respawn':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_type)
        elif self.subtype[2:] == '_object_update':
            return self.id + \
                hex_to_bytes({v: k for k, v in subtype_map.items()}[self.subtype]) + \
                int_to_bytes_little(4, self.timestamp) + \
                hex_to_bytes(self.object_type) + \
                hex_to_bytes(self.data['object_update_unk'])

    def __str__(self):
        return f"{self.name}; subtype:{self.subtype} " + \
                f"timestamp:{self.timestamp} object_type:{self.object_type} data:{self.data}"
