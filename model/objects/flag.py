
import asyncio

from model.objects.uyaobject import UyaObject
from medius.dme_packets import tcp_020C_info

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

    def reset(self):
        self.location = list(self.initial_location)
        self.holder = None

    def __str__(self):
        return f"Flag [{self.color}]; holder:{self.holder} id:{self.id} master:{self.master} owner:{self.owner} loc:{self.location}"