from collections import deque
import os
from utils.utils import *

class tcp_0004_tnwgamesettings:
    def __init__(self, unk1:str=None,
            p0_username:str='', p1_username:str='', p2_username:str='', p3_username:str='', p4_username:str='', p5_username:str='', p6_username:str='', p7_username:str='',
            p0_clan_tag:str='', p1_clan_tag:str='', p2_clan_tag:str='', p3_clan_tag:str='', p4_clan_tag:str='', p5_clan_tag:str='', p6_clan_tag:str='', p7_clan_tag:str='',
            unk2:str='',
            p0_bolt_modifier:str='', p1_bolt_modifier:str='', p2_bolt_modifier:str='', p3_bolt_modifier:str='', p4_bolt_modifier:str='', p5_bolt_modifier:str='', p6_bolt_modifier:str='', p7_bolt_modifier:str='',
            p0_bolt_skill:str='', p1_bolt_skill:str='', p2_bolt_skill:str='', p3_bolt_skill:str='', p4_bolt_skill:str='', p5_bolt_skill:str='', p6_bolt_skill:str='', p7_bolt_skill:str=''
            ):
        self.name = os.path.basename(__file__)
        self.id = b'\x00\x04'

        self.unk1 = unk1
        self.p0_username = p0_username
        self.p1_username = p1_username
        self.p2_username = p2_username
        self.p3_username = p3_username
        self.p4_username = p4_username
        self.p5_username = p5_username
        self.p6_username = p6_username
        self.p7_username = p7_username

        self.p0_clan_tag = p0_clan_tag
        self.p1_clan_tag = p1_clan_tag
        self.p2_clan_tag = p2_clan_tag
        self.p3_clan_tag = p3_clan_tag
        self.p4_clan_tag = p4_clan_tag
        self.p5_clan_tag = p5_clan_tag
        self.p6_clan_tag = p6_clan_tag
        self.p7_clan_tag = p7_clan_tag

        self.unk2 = unk2

        self.p0_bolt_modifier = p0_bolt_modifier
        self.p1_bolt_modifier = p1_bolt_modifier
        self.p2_bolt_modifier = p2_bolt_modifier
        self.p3_bolt_modifier = p3_bolt_modifier
        self.p4_bolt_modifier = p4_bolt_modifier
        self.p5_bolt_modifier = p5_bolt_modifier
        self.p6_bolt_modifier = p6_bolt_modifier
        self.p7_bolt_modifier = p7_bolt_modifier

        self.p0_bolt_skill = p0_bolt_skill
        self.p1_bolt_skill = p1_bolt_skill
        self.p2_bolt_skill = p2_bolt_skill
        self.p3_bolt_skill = p3_bolt_skill
        self.p4_bolt_skill = p4_bolt_skill
        self.p5_bolt_skill = p5_bolt_skill
        self.p6_bolt_skill = p6_bolt_skill
        self.p7_bolt_skill = p7_bolt_skill


    @classmethod
    def serialize(self, data: deque):
        unk1 = ''.join([data.popleft() for _ in range(36)])

        p0_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p1_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p2_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p3_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p4_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p5_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p6_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        p7_username = hex_to_str(''.join([data.popleft() for _ in range(16)]))

        p0_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p1_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p2_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p3_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p4_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p5_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p6_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))
        p7_clan_tag = hex_to_str(''.join([data.popleft() for _ in range(8)]))

        unk2 = ''.join([data.popleft() for _ in range(144)])

        p0_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p1_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p2_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p3_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p4_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p5_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p6_bolt_modifier = ''.join([data.popleft() for _ in range(4)])
        p7_bolt_modifier = ''.join([data.popleft() for _ in range(4)])

        p0_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p1_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p2_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p3_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p4_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p5_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p6_bolt_skill = ''.join([data.popleft() for _ in range(4)])
        p7_bolt_skill = ''.join([data.popleft() for _ in range(4)])

        return tcp_0004_tnwgamesettings(unk1, p0_username, p1_username, p2_username, p3_username, p4_username, p5_username, p6_username, p7_username,
            p0_clan_tag, p1_clan_tag, p2_clan_tag, p3_clan_tag, p4_clan_tag, p5_clan_tag, p6_clan_tag, p7_clan_tag,
            unk2,
            p0_bolt_modifier, p1_bolt_modifier, p2_bolt_modifier, p3_bolt_modifier, p4_bolt_modifier, p5_bolt_modifier, p6_bolt_modifier, p7_bolt_modifier,
            p0_bolt_skill, p1_bolt_skill, p2_bolt_skill, p3_bolt_skill, p4_bolt_skill, p5_bolt_skill, p6_bolt_skill, p7_bolt_skill
            )

    def to_bytes(self):
        raise Exception()

    def __str__(self):
        return f"{self.name}; unk1:{self.unk1} " + \
            f"p0_username:{self.p0_username} p1_username:{self.p1_username} p2_username:{self.p2_username} p3_username:{self.p3_username} p4_username:{self.p4_username} p5_username:{self.p5_username} p6_username:{self.p6_username} p7_username:{self.p7_username} " + \
            f"p0_clan_tag:{self.p0_clan_tag} p1_clan_tag:{self.p1_clan_tag} p2_clan_tag:{self.p2_clan_tag} p3_clan_tag:{self.p3_clan_tag} p4_clan_tag:{self.p4_clan_tag} p5_clan_tag:{self.p5_clan_tag} p6_clan_tag:{self.p6_clan_tag} p7_clan_tag:{self.p7_clan_tag} " + \
            f"unk2:{self.unk2} " + \
            f"p0_bolt_modifier:{self.p0_bolt_modifier} p1_bolt_modifier:{self.p1_bolt_modifier} p2_bolt_modifier:{self.p2_bolt_modifier} p3_bolt_modifier:{self.p3_bolt_modifier} p4_bolt_modifier:{self.p4_bolt_modifier} p5_bolt_modifier:{self.p5_bolt_modifier} p6_bolt_modifier:{self.p6_bolt_modifier} p7_bolt_modifier:{self.p7_bolt_modifier} " + \
            f"p0_bolt_skill:{self.p0_bolt_skill} p1_bolt_skill:{self.p1_bolt_skill} p2_bolt_skill:{self.p2_bolt_skill} p3_bolt_skill:{self.p3_bolt_skill} p4_bolt_skill:{self.p4_bolt_skill} p5_bolt_skill:{self.p5_bolt_skill} p6_bolt_skill:{self.p6_bolt_skill} p7_bolt_skill:{self.p7_bolt_skill}"
