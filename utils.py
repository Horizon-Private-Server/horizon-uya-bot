def bytes_to_int_little(data):
    return int.from_bytes(data, byteorder='little')

def bytes_to_hex(data:bytes):
    return data.hex().upper()

def bytes_from_hex(hex:str):
    return bytes(bytearray.fromhex(hex))

def int_to_bytes_little(bytelength, data, signed=False):
    return data.to_bytes(bytelength, 'little', signed=signed)

