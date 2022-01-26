def bytes_to_int_little(data):
    return int.from_bytes(data, byteorder='little')

def bytes_to_hex(data:bytes):
    return data.hex().upper()

def int_to_bytes_little(bytelength, data, signed=False):
    return data.to_bytes(bytelength, 'little', signed=signed)

def str_to_bytes(data: str, length: int) -> bytes:
    str_bytes = data
    assert(length > len(data))
    while (len(str_bytes) != length):
        str_bytes += '\0'
    return str_bytes.encode()

def hex_to_bytes(hex:str):
    return bytes(bytearray.fromhex(hex))

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
