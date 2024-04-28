import asyncio
import websockets
import json
import os
import argparse
import time
from datetime import datetime
import math


import sys
sys.path.append("..")

import logging
from logging import handlers

from collections import deque

from medius.dme_serializer import TcpSerializer as tcp_map
from medius.dme_serializer import UdpSerializer as udp_map
from medius.dme_serializer import packets_both_tcp_and_udp
from constants.constants import get_blitz_angle

from butils.utils import *

class Blarg:
    def __init__(self, config: dict):
        self._config = config

        self._logger = logging.getLogger('blarg')
        formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.getLevelName(config['logger']))
        self._logger.addHandler(sh)

        filehandler = logging.FileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)),'logs','blarg.log'), mode='w')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        self._logger.addHandler(filehandler)

        self._logger.setLevel(logging.DEBUG)

        self._recent_movement = None

    def run(self):
        asyncio.new_event_loop().run_until_complete(self.read_websocket())

    def process(self, packet: dict):
        '''
        Process json from Robo's websocket.
        Structure:
        {
            "type": udp/tcp
            "dme_world_id": int
            "src": the source player dme id
            "dst": the destination player dme id, -1 for sending to all
            "data": a hex string of the raw data
        }
        '''
        if self._config['src_filter'] != []:
            if packet['src'] not in self._config['src_filter']:
                return
        # Convert to list. E.g. '000102030405' -> ['00', '01', '02', '03', '04', '05']
        data = deque([packet['data'][i:i+2] for i in range(0,len(packet['data']),2)])

        '''
        There may be multiple messages in each message.
        So we have to read the current message, and see if there's any leftover
        data which would be another message
        '''
        # Keep reading until data is empty
        while len(data) != 0:
            packet_id = data.popleft() + data.popleft() # E.g. '0201'

            # if self._config['filter'] == packet_id:
            #     d = packet_id + ''.join(list(data))
            #     self._logger.info(f"{packet['type']} | {d} | {d[14:22]} | {bytes_to_int_little(hex_to_bytes(d[14:22]))}")

            # Check if the packet_id exists. If it does, serialize it
            if packet['type'] == 'tcp':
                if packet_id not in tcp_map.keys():
                    if self._config['warn_on_unknown'] == 'True':
                        self._logger.warning(f"Unknown {packet['type']} src:{packet['src']} packet id: {packet_id} | data: {packet['data']}")
                    break
                else:
                    if packet_id in packets_both_tcp_and_udp:
                        serialized = tcp_map[packet_id].serialize('tcp', data)
                    else:
                        serialized = tcp_map[packet_id].serialize(data)

            elif packet['type'] == 'udp':
                if packet_id not in udp_map.keys():
                    if self._config['warn_on_unknown'] == 'True':
                        self._logger.warning(f"Unknown {packet['type']} src:{packet['src']} packet id: {packet_id} | data: {packet['data']}")
                    break
                else:
                    if packet_id in packets_both_tcp_and_udp:
                        serialized = udp_map[packet_id].serialize('udp', data)
                    else:
                        serialized = udp_map[packet_id].serialize(data)

            if packet_id in self._config['exclude']:
                continue

            if packet_id == '0209':
                self._recent_movement = serialized.data

            if (self._config['filter'] == packet_id or self._config['filter'] == '') and self._config['log_serialized'] != 'False': # and packet_id not in ['0209', '0213']:
                #self._logger.info(f"{packet['src']} -> {packet['dst']} | {serialized}")

                if serialized.unk1 == '08':
                    self._logger.info(f"{packet['src']} -> {packet['dst']} | DEBUGGING ANGLES {self._recent_movement['cam3_x']} | {serialized.local_x_2} | {serialized.local_y_2} | {serialized.local_z_2} | {get_blitz_angle(self._recent_movement['cam3_x'])}")
                    #self._logger.info(f"{packet['src']} -> {packet['dst']} | {serialized} | {self._recent_movement}")


                # unk5 = serialized.unk5[4:]
                # unk6 = serialized.unk6[4:]
                # unk7 = serialized.unk7[4:]
                # unk5_int = hex_to_int_little(unk5)
                # unk6_int = hex_to_int_little(unk6)
                # unk7_int = hex_to_int_little(unk7)
                # # self._logger.info(f"{packet['src']} -> {packet['dst']} | {unk5} | {unk6} | {unk7} | ")
                # res = f'[{self._coord},[{unk5_int},{unk6_int:05d},{unk7_int:05d}]],'
                # print(res)


    async def read_websocket(self):
        uri = f"ws://{self._config['server_ip']}:8765"
        async with websockets.connect(uri,ping_interval=None) as websocket:
            while True:
                data = await websocket.recv()
                self._logger.debug(f"{data}")

                if self._config['fail_on_error'] == 'True':
                    for data_point in json.loads(data):
                        self.process(data_point)
                else:
                    try:
                        for data_point in json.loads(data):
                            #print(data_point)
                            self.process(data_point)
                    except:
                        self._logger.exception(f"error processing: {data_point}")

def scale_value(value):
    # Scale value from range 0-255 to range 0-180
    scaled_value = (value / 255) * 180
    return scaled_value

def read_config(target, config_file='config.json'):
    with open(config_file, 'r') as f:
        config = json.loads(f.read())
        config['server_ip'] = config[target]
        return config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Horizon's UYA Bot. (Thug)")
    parser.add_argument('--target', type=str, default='test', help='Use prod or test target')

    args = parser.parse_args()
    config = read_config(args.target)

    blarg = Blarg(config)
    blarg.run()
