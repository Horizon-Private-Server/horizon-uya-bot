from collections import deque
import math
import traceback


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
