
from collections import deque
from butils.utils import *
import os

from constants.constants import TEAM_MAP, SKIN_MAP

class tcp_0211_player_lobby_state_change:

    _ready_map = {
        '06': 'ready',
        '01': 'not ready',
        '00': 'no change',
        '02': 'broadcast not ready',
        '04': 'change team request',
        '08': 'unk, player in-game ready(?)'
    }

    def __init__(self, unk1:str='00000000',
                       team:str=None,
                       skin:str=None,
                       ready:str=None,
                       username:str=None,
                       unk2:str='0000000000000000000000'
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x11'
        self.unk1 = unk1
        self.team = team
        self.skin = skin
        self.username = username
        self.ready = ready
        self.unk2 = unk2

        assert self.team in TEAM_MAP.values()
        assert self.skin in SKIN_MAP.values()
        assert self.ready in self._ready_map.values()

    @classmethod
    def serialize(self, data: deque):
        # Length = 32
        unk1 = data.popleft() + data.popleft() + data.popleft() + data.popleft() #'00000000'

        team = TEAM_MAP[data.popleft()]
        skin = SKIN_MAP[data.popleft()]

        ready = data.popleft()
        ready = self._ready_map[ready]

        username = hex_to_str(''.join([data.popleft() for i in range(14)]))

        unk2 = ''.join([data.popleft() for i in range(11)])

        return tcp_0211_player_lobby_state_change(unk1=unk1, team=team, skin=skin, username=username, ready=ready, unk2=unk2)


    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1) + \
            hex_to_bytes({v: k for k, v in TEAM_MAP.items()}[self.team]) + \
            hex_to_bytes({v: k for k, v in SKIN_MAP.items()}[self.skin]) + \
            hex_to_bytes({v: k for k, v in self._ready_map.items()}[self.ready]) + \
            str_to_bytes(self.username, 14) + \
            hex_to_bytes(self.unk2)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} team:{self.team} " + \
                f"skin:{self.skin} ready:{self.ready} username:{self.username} unk2:{self.unk2}"
