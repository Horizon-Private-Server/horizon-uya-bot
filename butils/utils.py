from collections import deque
import math
import traceback
from copy import deepcopy

def bit_string_to_2_bytes_hex(bit_string):
    # Ensure the bit string is exactly 16 bits (2 bytes) long
    if len(bit_string) != 16:
        raise ValueError("Bit string must be exactly 16 bits long")

    # Split the bit string into 4-bit segments and convert each to a hex digit
    hex_string = ''.join(f'{int(bit_string[i:i+4], 2):x}' for i in range(0, 16, 4))
    
    return hex_string.upper()

def dequeue_to_str(d):
    a = deepcopy(d)
    res = ''
    while len(a) > 0:
        res += a.popleft()
    return res

def short_bytes_to_int(byte1, byte2):
    data = byte2 + byte1
    data = int(data, 16)
    return data

def bytes_to_str(data: bytes) -> str:
    res = ''
    for b in data:
        if b == 0x00:
            return res
        res += chr(b)
    return res

def bytes_to_int_little(data):
    return int.from_bytes(data, byteorder='little')

def bytes_to_hex(data:bytes):
    return data.hex().upper()

def int_to_bytes_little(bytelength, data, signed=False):
    return data.to_bytes(bytelength, 'little', signed=signed)

def str_to_bytes(data: str, length: int) -> bytes:
    if len(data) == length:
        return data.encode()

    if len(data) > length:
        return data[:length].encode()

    str_bytes = data
    assert(length > len(data))
    while (len(str_bytes) != length):
        str_bytes += '\0'
    return str_bytes.encode()

def hex_to_bytes(hex:str):
    return bytes(bytearray.fromhex(hex))

def rtpacket_to_bytes(packet: list):
    '''
    Create a byte array from an rt id and the
    byte arrays that go into that payload.
    If an arg is a dict, it is interpreted as a
    medius packet, and will be consolidated into
    the packet
    '''

    name = packet.pop(0)
    rtid = packet.pop(0)['rtid']
    result = b''
    for arg in packet:
        arg = list(arg.values())[0]
        if type(arg) == int:
            result += bytes([arg])
        # Medius internal packet
        elif type(arg) == list:
            arg.pop(0) # Remove the name for the mediuspacket
            for mediusarg in arg:
                mediusvalue = list(mediusarg.values())[0]
                if type(mediusvalue) == int:
                    result += bytes([mediusvalue])
                else:
                    result += bytes(mediusvalue)
        else:
            result += bytes(arg)
    return rtid + int_to_bytes_little(2, len(result)) + result


def dme_packet_to_bytes(packet: list):
    packet.pop(0)
    result = b''
    for d in packet:
        result += list(d.values())[0]
    return result

def dme_serialize(data: bytearray, data_dict: [dict], name: str) -> dict:
    '''Serialize the byte array based on the data dictionary
    '''
    results = {'packet': name}
    try:
        for pair in data_dict:
            if len(data) <= 0:
                break
            thisBytes = []

            if pair['n_bytes'] == None:
                while len(data) != 0:
                    thisBytes.append(data.pop(0))
            else:
                for _ in range(pair['n_bytes']):
                    thisBytes.append(data.pop(0))

            if pair['cast'] == None:
                results[pair['name']] = bytes(thisBytes)
            else:
                results[pair['name']] = pair['cast'](bytes(thisBytes))
    except:
        print("ERROR SERIALIZING: " + data.hex().upper())
        traceback.print_exc()
    return results


def serialize(data: bytes, data_dict: [dict], name: str) -> dict:
    '''Serialize the byte array based on the data dictionary
    '''
    byteList = deque(data)
    results = {'packet': name}
    try:
        for pair in data_dict:
            if len(byteList) <= 0:
                break
            thisBytes = []

            if pair['n_bytes'] == None:
                while len(byteList) != 0:
                    thisBytes.append(byteList.popleft())
            else:
                for _ in range(pair['n_bytes']):
                    thisBytes.append(byteList.popleft())

            if pair['cast'] == None:
                results[pair['name']] = bytes(thisBytes)
            else:
                results[pair['name']] = pair['cast'](bytes(thisBytes))
    except:
        print("ERROR SERIALIZING: " + data.hex().upper())
        traceback.print_exc()
    return results

def hex_to_int_little(hex: str):
    return bytes_to_int_little(hex_to_bytes(hex))

def hex_to_str(data: str):
    return bytes_to_str(hex_to_bytes(data))

def hex_to_bit_string(hex_string):
    # Convert each hex character to a 4-bit binary string
    binary_string = ''.join(f'{int(c, 16):04b}' for c in hex_string)
    return binary_string

############ Math functions

import math
import numpy as np
first_keys = np.array(list(reversed(np.arange(-179,1)))).astype(int)
first_vals = np.linspace(127,0, 180).astype(int)
first_angle_map = dict(zip(first_keys, first_vals))

second_keys = np.array(list(reversed(np.arange(0,181)))).astype(int)
second_vals = np.linspace(254,128, 181).astype(int)
second_angle_map = dict(zip(second_keys, second_vals))

def calculate_angle(source_coord, dest_coord):
    # UYA uses angles from 0 -> 254. We need to translate the 0->180|-179->0 to this coordinate system
    degrees = int(math.degrees(math.atan2(dest_coord[1]-source_coord[1],dest_coord[0]-source_coord[0])))
    if -179 <= degrees <= 0:
        return int(first_angle_map[degrees])
    elif 1 <= degrees <= 180:
        return int(second_angle_map[degrees])

    raise Exception(f"Invalid coordinates! Unable to calculate angle! source_coord:{source_coord} dest_coord:{dest_coord}")

def calculate_distance(source_coord, dest_coord):
    return math.dist(source_coord, dest_coord)

def find_closest_node_from_list(src, dsts):
    min_dist = 999999999999
    min_idx = None
    for i,dst in enumerate(dsts):
        edist = math.dist(src, dst)
        if edist < min_dist:
            min_dist = edist
            min_idx = i
    return min_idx





# Calculate the strafe angle between three points.
'''
perpendicular left/right strafe between 70 and 90 
forwards movement < 30
backwards movement > 160
forward strafe = between 30 and 70
backward strafe = between 110 and 160


standard joystick:
forward = 90 | 0
forward right = 180 | 27
forward left = 14 | 19

right strafe = 180 | 90
left stafe = 0 | 90

backward = 90 | 180
backward right = 157 | 174
backward left = 21 | 172
'''
def strafe_joystick_input(strafe_angle, direction):
    # Pure left/right strafe
    strafe_angle_min = 70
    strafe_angle_max = 110
    if strafe_angle_min <= strafe_angle <= strafe_angle_max:
        if direction == 'left':
            return [0, 90]
        elif direction == 'right':
            return [180, 90]
    
    pure_forward_back_scale = 15
    # Pure forward
    if strafe_angle < (0+pure_forward_back_scale):
        return [90,0]
    # Pure backwards
    if strafe_angle > (180-pure_forward_back_scale):
        return [90,180]

    # Mixed forward movement
    if strafe_angle < 90:
        # 0 more forward, 90 more left
        if direction == 'left': 
            # (forward) [90, 0] -> (left) [0, 90]

            x_val = scale_strafe_angle(strafe_angle, pure_forward_back_scale, strafe_angle_min, -50, 0)
            y_val = scale_strafe_angle(strafe_angle, pure_forward_back_scale, strafe_angle_min, 0, 40)
            return [x_val, y_val]
        elif direction == 'right': # (forward) [90,0] -> (right) [180, 90]
            # Deadzone from 90->130
            x_val = scale_strafe_angle(strafe_angle, pure_forward_back_scale, strafe_angle_min, 130, 180)
            # Deadzone from 30-90
            y_val = scale_strafe_angle(strafe_angle, pure_forward_back_scale, strafe_angle_min, 0, 30)
            return [x_val, y_val]
            #return [180, 27]

    # Mixed backwards movement
    if strafe_angle > 90:
        if direction == 'left': # (backward) [90,180] -> (left) [0, 90] 
            x_val = scale_strafe_angle(strafe_angle, strafe_angle_max, 180-pure_forward_back_scale, -40, 0)
            y_val = scale_strafe_angle(strafe_angle, strafe_angle_max, 180-pure_forward_back_scale, -180, -150)
            return [x_val, y_val]
            #return [21, 172]
        elif direction == 'right': # (backward) [90,180] ->  (right) [180, 90]
            x_val = scale_strafe_angle(strafe_angle, strafe_angle_max, 180-pure_forward_back_scale, 130, 180)
            y_val = scale_strafe_angle(strafe_angle, strafe_angle_max, 180-pure_forward_back_scale, -180, -140)
            return [x_val, y_val]
            #return [157, 174]

def scale_strafe_angle(strafe_angle, strafe_angle_min, strafe_angle_max, new_min, new_max):
    # Calculate the relative position of input_number within the input range
    relative_position = (strafe_angle - strafe_angle_min) / (strafe_angle_max - strafe_angle_min)
    
    # Scale this relative position to the output range
    scaled_value = new_min + relative_position * (new_max - new_min)
    
    return abs(int(scaled_value))

def compute_strafe_angle(P1, P2, P3):
    # Vector from P1 to P2
    try:
        v1 = (P2[0] - P1[0], P2[1] - P1[1])
        
        # Vector from P1 to P3
        v2 = (P3[0] - P1[0], P3[1] - P1[1])
        
        # Calculate dot product of v1 and v2
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        
        # Calculate magnitudes of v1 and v2
        mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        # Calculate cosine of the angle between v1 and v2
        cos_theta = dot_product / (mag_v1 * mag_v2)
        
        # Prevent domain errors
        cos_theta = max(-1, min(1, cos_theta))

        # Calculate the angle in radians
        angle_rad = math.acos(cos_theta)
        
        # Convert angle from radians to degrees
        angle_deg = math.degrees(angle_rad)

    except ZeroDivisionError as e:
        return 90

    return angle_deg

def get_forward_direction(P1, P2, P3):
    # Convert points to numpy arrays for easier computation
    P1 = np.array(P1)
    P2 = np.array(P2)
    P3 = np.array(P3)
    
    # Calculate direction vector from P1 to P2
    dir_P1_to_P2 = P2 - P1
    
    # Calculate vector from P3 to P1
    vector_P3_to_P1 = P1 - P3
    
    # Calculate difference vector from P1 to P2
    delta_vector = P2 - P1
    
    # Compute dot product to determine direction relative to P3
    dot_product = np.dot(delta_vector, vector_P3_to_P1)

    if dot_product > 0:
        return 'backward'
    else:
        return 'forward'
    

def get_strafe_direction(P1, P2, P3):
    # Convert points to numpy arrays for easier computation
    P1 = np.array(P1)
    P2 = np.array(P2)
    P3 = np.array(P3)
    
    # Calculate direction vector from P1 to P2
    dir_P1_to_P2 = P2 - P1
    
    # Calculate vector from P3 to P1
    vector_P3_to_P1 = P1 - P3
    
    # Project dir_P1_to_P2 onto the plane perpendicular to vector_P3_to_P1
    perpendicular_component = dir_P1_to_P2 - np.dot(dir_P1_to_P2, vector_P3_to_P1) / np.dot(vector_P3_to_P1, vector_P3_to_P1) * vector_P3_to_P1
    
    # Compute cross product between vector_P3_to_P1 and dir_P1_to_P2
    cross_product = np.cross(vector_P3_to_P1, dir_P1_to_P2)
    
    # Determine the sign of the z-component of the cross product to determine direction
    if cross_product[2] > 0:
        return "right"
    # elif cross_product[2] < 0:
    return "left"


def scale_255_to_180(value):
    # Ensure value is within the range 0-255
    value = max(0, min(255, value))
    
    # Scale the value from 0-255 to 0-180
    scaled_value = (value / 255) * 180
    
    return int(scaled_value)

def scale_180_to_255(value):
    # Ensure value is within the range 0-180
    value = max(0, min(180, value))
    
    # Scale the value from 0-180 to 0-255
    scaled_value = (value / 180) * 255
    
    return int(scaled_value)  # Convert to integer for whole number result
