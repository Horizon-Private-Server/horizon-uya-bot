from collections import deque
from utils.utils import *
import os


team_map = {
    '00': 'blue',
    '01': 'red',
    '02': 'green',
    '03': 'orange',
    '04': 'yellow',
    '05': 'purple',
    '06': 'aqua',
    '07': 'pink',
    'FF': 'NA'
}
skin_map = {
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
    '15': 'dan',
    'FF': 'NA'
}

player_id_map = {
    '0000': -1,
    '0100': 0,
    '0300': 1,
}

class tcp_0003_broadcast_lobby_state:
    def __init__(self, data:dict):
        self.name = os.path.basename(__file__).strip(".py")
        self.id = b'\x00\x03'
        self.data = data

    @classmethod
    def serialize(self, data: deque):
        # Length is #messages * 17
        packet = {}
        packet['unk1'] = data.popleft() # 01

        packet['num_messages'] = bytes_to_int_little(hex_to_bytes(data.popleft()))

        packet['src'] = player_id_map[data.popleft() + data.popleft()]

        for i in range(packet['num_messages']):
            sub_message = {}
            broadcast_type = data.popleft()
            #assert broadcast_type in ['02','03','05']

            if broadcast_type == '05': # Ready/Unready
                sub_message['type'] = 'ready/unready'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = val == '06'
            elif broadcast_type == '03': # Color
                sub_message['type'] = 'colors'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = team_map[val]
            elif broadcast_type == '02': # Skins
                sub_message['type'] = 'skins'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    sub_message[f'p{player_id}'] = skin_map[val]
            elif broadcast_type == '07':
                sub_message['type'] = '07_unk'
                sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(4)]))
            elif broadcast_type == '09':
                sub_message['type'] = 'timer_update'
                sub_message['time'] = hex_to_int_little(''.join([data.popleft() for i in range(2)]))
            else:
                raise Exception(f'{broadcast_type} not known!')

            packet[f'msg{i}'] = sub_message

        return tcp_0003_broadcast_lobby_state(packet)

    def to_bytes(self):
        raise Exception()

    def __str__(self):
        return f"{self.name}; data:{self.data}"
