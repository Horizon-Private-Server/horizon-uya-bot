from collections import deque

def bytes_to_str(data: bytes) -> str:
    res = ''
    for b in data:
        if b == 0x00:
            return res
        res += chr(b)
    return

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
