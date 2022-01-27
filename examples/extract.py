import numpy as np
from numba import jit


@jit(nopython=True)
def process(input_buf, data):

    results = []
    buf = None

    if input_buf is not None:
        data = np.concatenate((input_buf,data))

    while True:
        len_bytes = data[1:3] # Reverse it
        len_bytes = len_bytes[0] + (len_bytes[1]*16*16) # calculate length of packet

        packet_length = 1 + 2 + len_bytes
        
        if (data[0] & 0xFF) >= 128: # Encrypted. So we need to add the hash to the packet length
            packet_length += 4

        if packet_length == data.size: # Perfect fit
            results.append(data)
            return buf, results
        elif packet_length > data.size: # This happens when the packet is cut-off
            buf = data
            return buf, results
        elif packet_length < data.size: # Multiple packets here
            results.append(data[0:packet_length])
            data = data[packet_length:]
        else:
            raise Exception("Unknown error!")

    return buf, results


class RtBufferDeframer():
    def __init__(self):
        self._buffer = None

    def deframe(self, data: bytes):
        data = np.frombuffer(data, dtype=np.uint8, count=-1)
        buf, results = process(self._buffer, data)
        self._buffer = buf
        results = [result.tobytes() for result in results]
        return results


    @classmethod
    def basic_deframe(self, data: bytes):
        deframer = RtBufferDeframer()
        return deframer.deframe(data)

def hex_to_bytes(hex:str):
    return bytes(bytearray.fromhex(hex))

def bytes_to_hex(data:bytes):
    return data.hex().upper()

lines = []
with open('all.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if "dmetcp" in line:
            protocol = 'TCP'
            if '34465' in line and ' I ' in line:
                player = 'P0'
            elif '46719' in line and ' I ' in line:
                player = 'P1'
        else:
            protocol = 'UDP'
            if '57069' in line and ' I ' in line:
                player = 'P0'
            elif '52976' in line and ' I ' in line:
                player = 'P1'
        
        data = line.split(" | ")[-1]
        data = hex_to_bytes(data)
        packets = RtBufferDeframer().deframe(data)
        for packet in packets:
            print(f"{protocol} {player} {bytes_to_hex(packet)}")

           

