import asyncio
import websockets
import json
import os
import argparse
from datetime import datetime

import sys
sys.path.append("..")

import logging
from logging import handlers

from collections import deque

from medius.dme_serializer import TcpSerializer as tcp_map
from medius.dme_serializer import UdpSerializer as udp_map

from butils.utils import *

with open("config.json",'r') as f:
    config = json.loads(f.read())
ip = config['test']

async def read_websocket():
    
    p1_counter = 0
    p2_counter = 0

    start_time = datetime.now()
    counter_max = 10000


    uri = f"ws://{ip}:8765"
    async with websockets.connect(uri,ping_interval=None) as websocket:
        while True:
            data = await websocket.recv()
            for data_point in json.loads(data):
                if '0209' in json.dumps(data_point) and 'udp' in json.dumps(data_point):
                    print(datetime.now(), data_point)

                    if '"src": 0' in json.dumps(data_point):
                        p1_counter += 1
                    elif '"src": 1' in json.dumps(data_point):
                        p2_counter += 1

                if p1_counter > counter_max or p2_counter > counter_max:
                    print(f"P1COUNTER: {p1_counter}")
                    print(f"P2COUNTER: {p2_counter}")
                    end_time = datetime.now()

                    print(f"Total time: {(end_time - start_time).total_seconds()}") 
                    return
            
asyncio.new_event_loop().run_until_complete(read_websocket())

