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

import argparse
parser = argparse.ArgumentParser(description='dme parser')
parser.add_argument('--log', help='log', required=True)
parser.add_argument('--out', help='out', required=True)
cli_args = parser.parse_args()


tcp_found_ports = []
udp_found_ports = []

lines = []
with open(cli_args.log, 'r') as f:
    for line in f:
        line = line.strip()
        if 'robo.dme' not in line:
            continue
        if ' I ' not in line:
            continue

        port = line.split(") | ")[0].split()[-1]
        if 'robo.dmetcp' in line:
            if port not in tcp_found_ports:
                tcp_found_ports.append(port)
                lines.append(f"[ ----- P{tcp_found_ports.index(port)} connected -----]")
            protocol = 'TCP'
        else:
            if port not in udp_found_ports:
                udp_found_ports.append(port)
            protocol = 'UDP'

        data = line.split(" | ")[-1]
        data = hex_to_bytes(data)
        packets = RtBufferDeframer().deframe(data)
        for packet in packets:
            if bytes_to_hex(packet)[0:2] in ['0D', '0E', '05', '10']: # random packets not necessary
                continue
            lines.append(f"{protocol} P{tcp_found_ports.index(port) if protocol == 'TCP' else udp_found_ports.index(port)} {bytes_to_hex(packet)}")

with open(cli_args.out, 'w') as f:
    for line in lines:
        if "connected" in line:
            f.write(f"{line}\n\n")
            continue

        data = line.split()[-1]  
        b_type = data[0:2]
        if b_type == '02':
            f.write(f"{' '.join(line.split()[0:2])} {data[0:6]}\n{data[6:]}\n\n")
        elif b_type == '03':
            f.write(f"{' '.join(line.split()[0:2])} {data[0:10]}\n{data[10:]}\n\n")
        else:
            f.write(f"{line}\n\n")


         
