from collections import deque
from butils.utils import *
import os

from constants.constants import ANIMATION_MAP

class udp_0209_movement_update:
    def __init__(self, data:dict):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x09'
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        results = {}

        results['r1'] = data.popleft() # Rotation 1
        results['cam1_y'] = int(data.popleft(), 16)
        results['cam1_x'] = int(data.popleft(), 16)
        results['vcam1_y'] = data.popleft() # Vehicle camera rotation y
        results['r2'] = data.popleft()
        results['cam2_y'] = int(data.popleft(), 16)
        results['cam2_x'] = int(data.popleft(), 16)
        results['vcam2_y'] = data.popleft() # Vehicle camera rotation y
        results['r3'] = data.popleft()
        results['cam3_y'] = int(data.popleft(), 16)
        results['cam3_x'] = int(data.popleft(), 16)
        results['v_drv'] = data.popleft() # 1 if the driver of the vehicle, 0 if passenger
        results['r4'] = data.popleft()
        results['cam4_y'] = int(data.popleft(), 16)
        results['cam4_x'] = int(data.popleft(), 16)
        results['buffer'] = data.popleft()

        x = short_bytes_to_int(data.popleft(), data.popleft())
        y = short_bytes_to_int(data.popleft(), data.popleft())
        z = short_bytes_to_int(data.popleft(), data.popleft())
        results['coord'] = [x,y,z]
        # print(bytes_to_hex(int_to_bytes_little(2, results['coord'][0])),   bytes_to_hex(int_to_bytes_little(2, results['coord'][1])),  bytes_to_hex(int_to_bytes_little(2, results['coord'][2])))
        #print(results['coord'])

        results['packet_num'] = int(data.popleft(), 16)
        results['flush_type'] = int(data.popleft(), 16) # flush type -- if there are buttons or total flush
        results['left_joystick_x'] = scale_255_to_180(hex_to_int_little(''.join([data.popleft() for i in range(1)])))
        results['left_joystick_y'] = scale_255_to_180(hex_to_int_little(''.join([data.popleft() for i in range(1)])))
        results['left_joystick_repeats'] = ''.join([data.popleft() for i in range(6)])

        # Tests
        assert results['buffer'] == '00'

        ## Parse the button and flush
        #


        if results['cam4_x'] == 0 and results['cam4_y'] == 0:
            results['type'] = 'vehicle movement'
        else:
            results['type'] = 'movement'

        # No buttons or stand still update
        if results['flush_type'] == 0:
            pass
        # Flush type of 1 means no buttons were pressed, and the user is standing still.
        # It looks like there are 17 bytes in this that contain xyz coordinates and camera
        elif results['flush_type'] == 1:
            results['flush'] = ''.join([data.popleft() for i in range(17)])

        # 16 does not have the extra flush data. But it's impossible to differentiate
        # between when there are buttons + extra packet e.g. 020E
        elif results['flush_type'] > 1:
            if len(data) > 17:
                results['button'] = ''.join([data.popleft() for i in range(len(data)-17)]) # this is wrong
                results['flush'] = ''.join([data.popleft() for i in range(17)])
# 2022-03-09 14:36:32,713 blarg | INFO | 0 | udp_0209_movement_update; data:{'r1': '7F', 'cam1_y': 128, 'cam1_x': 46, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 128, 'cam2_x': 46, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 128, 'cam3_x': 46, 'v_drv': '00', 'r4': '7F', 'cam4_y': 128, 'cam4_x': 46, 'buffer': '00', 'coord': [21629, 24276, 2174], 'packet_num': 76, 'flush_type': 16, 'left_joystick': '5806580658065806', 'type': 'movement', 'button': 'B673020E03004008D7385100FFFFFFFF0FA2A843D510BD', 'flush': '4313B10B4279DE9F437B18AA437A950B42'}


            elif len(data) < 17:
                results['button'] = ''.join([data.popleft() for i in range(len(data))])
            elif len(data) == 17:
                results['flush'] = ''.join([data.popleft() for i in range(17)])

        ## Flush type / button / animation debugging
        # if 'flush' in results.keys():
        #     if 'button' in results.keys():
        #         print(results['coord'], results['button'], results['left_joystick'], results['flush_type'], results['flush'])
        #     else:
        #         print(results['coord'], results['left_joystick'], results['flush_type'], results['flush'])
        # elif 'button' in results.keys():
        #     print(results['coord'], results['button'], results['left_joystick'], results['flush_type'])

        ## Camera debugging
        # if 'button' in results.keys():
        #     del results['button']
        # if 'flush' in results.keys():
        #     del results['flush']
        # del results['type']
        # del results['left_joystick']

        # keys = ['coord', 'cam1_y', 'cam1_x', 'cam2_y', 'cam2_x', 'cam3_y', 'cam3_x', 'cam4_y', 'cam4_x']
        # test = [results.get(key) for key in keys]
        # print(test)

        return udp_0209_movement_update(results)


    def to_bytes(self):
        res = self.id + \
            hex_to_bytes(self.data['r1']) + \
            int_to_bytes_little(1, self.data['cam1_y']) + \
            int_to_bytes_little(1, self.data['cam1_x']) + \
            hex_to_bytes(self.data['vcam1_y']) + \
            hex_to_bytes(self.data['r2']) + \
            int_to_bytes_little(1, self.data['cam2_y']) + \
            int_to_bytes_little(1, self.data['cam2_x']) + \
            hex_to_bytes(self.data['vcam2_y']) + \
            hex_to_bytes(self.data['r3']) + \
            int_to_bytes_little(1, self.data['cam3_y']) + \
            int_to_bytes_little(1, self.data['cam3_x']) + \
            hex_to_bytes(self.data['v_drv']) + \
            hex_to_bytes(self.data['r4']) + \
            int_to_bytes_little(1, self.data['cam4_y']) + \
            int_to_bytes_little(1, self.data['cam4_x']) + \
            hex_to_bytes(self.data['buffer']) + \
            int_to_bytes_little(2, int(self.data['coord'][0])) + \
            int_to_bytes_little(2, int(self.data['coord'][1])) + \
            int_to_bytes_little(2, int(self.data['coord'][2])) + \
            int_to_bytes_little(1, self.data['packet_num']) + \
            int_to_bytes_little(1, self.data['flush_type'])

        if 'left_joystick_x' in self.data.keys():
            joystick_x = int_to_bytes_little(1, scale_180_to_255(self.data['left_joystick_x']))
            joystick_y = int_to_bytes_little(1, scale_180_to_255(self.data['left_joystick_y']))
            res += joystick_x + joystick_y + joystick_x + joystick_y + joystick_x + joystick_y + joystick_x + joystick_y
        else:
            res += hex_to_bytes('7F7F7F7F7F7F7F7F')

        if 'animation' in self.data.keys():
            res += hex_to_bytes(ANIMATION_MAP[self.data['animation']])
        return res

    def __str__(self):
        return f"{self.name}; data:{self.data}"
