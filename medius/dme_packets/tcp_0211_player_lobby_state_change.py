from collections import deque

from utils.utils import *

class tcp_0211_player_lobby_state_change:
    def __init__(self):
        pass

    def serialize(self, data: deque):
        # Length = 32
        assert data.popleft() + data.popleft() + data.popleft() + data.popleft() == '00000000'
        packet_data = {}

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
        packet_data['team'] = team_map[data.popleft()]

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
        packet_data['skin'] = skin_map[data.popleft()]

        player_ready = data.popleft()
        if player_ready == '06':
            packet_data['ready'] = 'ready'

            account_name = ''.join([data.popleft() for i in range(14)])
            packet_data['username'] = bytes_to_str(bytes_from_hex(account_name))
            assert ''.join([data.popleft() for i in range(11)]) == '0000000000000000000000'

        elif player_ready == '01':
            packet_data = {'ready': 'not ready'}
            leftovers = ''.join([data.popleft() for i in range(25)])
            assert leftovers == '00000000000000000000000000000000000000000000000000'
        elif player_ready == '00':
            packet_data['ready'] = 'no change'
        elif player_ready == '02':
            packet_data = {'ready': 'broadcast not ready'}
            leftovers = ''.join([data.popleft() for i in range(25)])
            #assert leftovers == '00290000003100000044641A00000000000100000000000000'
        elif player_ready == '04':
            # Team change request
            packet_data = {'ready': 'change team request'}
        else:
            raise Exception(f"Unknown player ready type: {player_ready}")

        return packet_data
