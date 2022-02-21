from collections import deque
from utils.utils import *


class tcp_0003_broadcast_lobby_state:
    def __init__(self):
        pass

    def serialize(self, data: deque):
        # Length is #messages * 17
        #assert data.popleft() == '01' # unknown
        data.popleft() ## Unknown

        num_messages = bytes_to_int_little(bytes_from_hex(data.popleft()))

        # TODO: why is this here???
        if num_messages == 9:
            data.clear()

        data.popleft() ## unknown
        assert data.popleft() == '00'
        team_map = {
            '00': 'blue',
            '01': 'red',
            '02': 'green',
            '03': 'orange',
            '04': 'yellow',
            '05': 'purple',
            '06': 'aqua',
            '07': 'pink'
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
            '15': 'dan'
        }
        messages = []
        result = {'n_messages': num_messages}
        for i in range(num_messages):
            packet = {}
            broadcast_type = data.popleft()
            #assert broadcast_type in ['02','03','05']

            if broadcast_type == '05': # Ready/Unready
                packet['type'] = 'ready/unready'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    packet[f'p{player_id+1}'] = val == '06'
            elif broadcast_type == '03': # Color
                packet['type'] = 'colors'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    if val != 'FF':
                        packet[f'p{player_id+1}'] = team_map[val]
            elif broadcast_type == '02': # Skins
                packet['type'] = 'skins'
                for player_id in range(8):
                    val = data.popleft()
                    data.popleft()
                    if val != 'FF':
                        packet[f'p{player_id+1}'] = skin_map[val]
            else:
                data.clear() # TODO: it seems there are other broadcast types here, but they are unknown
                break
            result[f'msg_{i+1}'] = packet

        return result
