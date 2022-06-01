from collections import deque
from butils.utils import *
import os

from constants.constants import TEAM_MAP, SKIN_MAP

class tcp_0210_player_joined:
    def __init__(self, type:int=1,
                       account_id:int=None,
                       rank:str='00C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF43',
                       unk1:str='00000000',
                       skin1:str=None,
                       skin2:str=None,
                       username:str=None, # 14 len
                       unk2:str='0000',
                       username2:str=None, # 12 len
                       unk3:str='32000000',
                       clan_tag:str='',
                       unk4:str='00000000'
                       ):

        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x02\x10'
        self.type = type
        self.account_id = account_id
        self.rank = rank
        self.unk1 = unk1
        self.skin1 = skin1
        self.skin2 = skin2
        self.username = username
        self.unk2 = unk2
        self.username2 = username2
        self.unk3 = unk3
        self.clan_tag = clan_tag
        self.unk4 = unk4

    @classmethod
    def serialize(self, data: deque):
        type = hex_to_int_little(''.join([data.popleft() for i in range(4)])) # usually 1
        account_id = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
        rank = ''.join([data.popleft() for i in range(32)])
        unk1 = ''.join([data.popleft() for i in range(4)]) #00000000
        skin1 = SKIN_MAP[data.popleft()]; data.popleft();
        skin2 = SKIN_MAP[data.popleft()]; data.popleft();
        username = hex_to_str(''.join([data.popleft() for i in range(14)]))
        unk2 = ''.join([data.popleft() for i in range(2)]) # 0034 /
        username2 = hex_to_str(''.join([data.popleft() for i in range(12)]))
        unk3 = ''.join([data.popleft() for i in range(4)])
        clan_tag = ''.join([data.popleft() for i in range(4)])
        unk4 = ''.join([data.popleft() for i in range(4)])
        return tcp_0210_player_joined(type, account_id, rank, unk1, skin1, skin2, username, unk2, username2, unk3, clan_tag, unk4)

    def to_bytes(self):
        return self.id + \
            int_to_bytes_little(4, self.type) + \
            int_to_bytes_little(4, self.account_id) + \
            hex_to_bytes(self.rank) + \
            hex_to_bytes(self.unk1) + \
            hex_to_bytes({v: k for k, v in SKIN_MAP.items()}[self.skin1] + '00') + \
            hex_to_bytes({v: k for k, v in SKIN_MAP.items()}[self.skin2] + '00') + \
            str_to_bytes(self.username, 14) + \
            hex_to_bytes(self.unk2) + \
            str_to_bytes(self.username2, 12) + \
            hex_to_bytes(self.unk3) + \
            str_to_bytes(self.clan_tag, 4) + \
            hex_to_bytes(self.unk4)

    def __str__(self):
        return f"{self.name}; type:{self.type} account_id:{self.account_id} " + \
                f"rank:{self.rank} unk1:{self.unk1} skin1:{self.skin1} skin2:{self.skin2} username:{self.username} " + \
                f"unk2:{self.unk2} username2:{self.username2} unk3:{self.unk3} clan_tag:{self.clan_tag} unk4:{self.unk4}"
