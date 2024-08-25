
import asyncio

from model.objects.uyaobject import UyaObject
from medius.dme_packets import tcp_020C_info
from butils.utils import *
from datetime import datetime


import logging
logger = logging.getLogger('thug.flag')
logger.setLevel(logging.INFO)


flag_map = {
    'marcadia_palace': {
        'red': {
            'id': '131000F7',
            'location': [34453, 53970, 7361],
        },
        'blue': {
            'id': '141000F7',
            'location': [26807, 54004, 7362],
        },
    },
    'hoven_gorge': {
        'red': {
            'id': '4B1000F7',
            'location': [11435, 9727, 4348],
        },
        'blue': {
            'id': '4C1000F7',
            'location': [21374, 22588, 4439],
        },
    },
    'command_center': {
        'red': {
            'id': '131000F7',
            'location': [0,0,0],
        },
        'blue': {
            'id': '141000F7',
            'location': [0,0,0],
        },
    },
    'aquatos_sewers': {
        'red': {
            'id': '121000F7',
            'location': [0,0,0],
        },
        'blue': {
            'id': '131000F7',
            'location': [0,0,0],
        },
    },
    'blackwater_docks': {
        'red': {
            'id': '441000F7',
            'location': [0,0,0],
        },
        'blue': {
            'id': '431000F7',
            'location': [0,0,0],
        },
    },
    'bakisi_isles': {
        'red': {
            'id': '441000F7',
            'location': [0,0,0],
        },
        'blue': {
            'id': '431000F7',
            'location': [0,0,0],
        },
    },
}

#
   # def __init__(self, model, id=-1, location=[0,0,0], master=0, owner=0):

class Flag(UyaObject):
    def __init__(self, model, color, map, master=0, owner=0):
        super().__init__(model, master=master, owner=owner)
        self.color = color
        self.map = map
        self.location = flag_map[map][color]['location']
        self.initial_location = list(flag_map[map][color]['location'])
        self.id = flag_map[map][color]['id']
        self.holder = None
        self.recent_droptime = datetime.now()

    def reset(self):
        self.location = list(self.initial_location)
        self.holder = None

    def is_at_base(self):
        return self.holder == None and calculate_distance(self.location, self.initial_location) < 50

    def dropped(self, location):
        self.holder = None
        self.location = location
        self.recent_droptime = datetime.now()

    def is_capture(self, location):
        return calculate_distance(location, self.initial_location) < 150

    def is_recent_drop(self):
        return (datetime.now() - self.recent_droptime).total_seconds() < 1.75
    
    def is_dropped(self):
        return self.holder == None and not self.is_at_base()

    def __str__(self):
        return f"Flag [{self.color}]; holder:{self.holder} id:{self.id} master:{self.master} owner:{self.owner} loc:{self.location}"