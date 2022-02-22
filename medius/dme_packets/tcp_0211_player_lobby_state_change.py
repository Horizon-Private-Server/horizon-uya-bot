
from collections import deque
from utils.utils import *
import os

class tcp_0211_player_lobby_state_change:
    _team_map = {
        '00': 'blue',
        '01': 'red',
        '02': 'green',
        '03': 'orange',
        '04': 'yellow',
        '05': 'purple',
        '06': 'aqua',
        '07': 'pink'
    }
    _skin_map = {
        '00': 'ratchet',
        '01': 'robo',
        '02': 'thug',
        '03': 'tyhrranoid',
        '04': 'blarg',
        '05': 'ninja',
        '06': 'snow man',
        '07': 'bruiser',
        '08': 'gray',
        '09': 'hotbot',
        '0A': 'gladiola',
        '0B': 'evil clown',
        '0C': 'beach bunny',
        '0D': 'robo rooster',
        '0E': 'buginoid',
        '0F': 'branius',
        '10': 'skrunch',
        '11': 'bones',
        '12': 'nefarious',
        '13': 'trooper',
        '14': 'constructobot',
        '15': 'dan'
    }

    _ready_map = {
        '06': 'ready',
        '01': 'not ready',
        '00': 'no change',
        '02': 'broadcast not ready',
        '04': 'change team request'
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

        assert self.team in self._team_map.values()
        assert self.skin in self._skin_map.values()
        assert self.ready in self._ready_map.values()

    @classmethod
    def serialize(self, data: deque):
        # Length = 32
        unk1 = data.popleft() + data.popleft() + data.popleft() + data.popleft() #'00000000'

        team = self._team_map[data.popleft()]
        skin = self._skin_map[data.popleft()]

        ready = data.popleft()
        if ready == '06':
            ready = 'ready'
        elif ready == '01':
            ready = 'not ready'
        elif ready == '00':
            ready = 'no change'
        elif ready == '02':
            ready = 'broadcast not ready'
        elif ready == '04':
            ready = 'change team request'

        username = hex_to_str(''.join([data.popleft() for i in range(14)]))

        unk2 = ''.join([data.popleft() for i in range(11)])

        return tcp_0211_player_lobby_state_change(unk1=unk1, team=team, skin=skin, username=username, ready=ready, unk2=unk2)


    def to_bytes(self):
        return self.id + \
            hex_to_bytes(self.unk1) + \
            hex_to_bytes({v: k for k, v in self._team_map.items()}[self.team]) + \
            hex_to_bytes({v: k for k, v in self._skin_map.items()}[self.skin]) + \
            hex_to_bytes({v: k for k, v in self._ready_map.items()}[self.ready]) + \
            str_to_bytes(self.username, 14) + \
            hex_to_bytes(self.unk2)

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} team:{self.team} " + \
                f"skin:{self.skin} player_ready:{self.ready} username:{self.username} unk2:{self.unk2}"
