import requests
import time

def convert_to_hex(num):
    # Convert the number to hexadecimal with leading zeros and format as a string
    hex_str = f"{num:02X}"
    return hex_str

from itertools import cycle

class CircularByteQueue:
    def __init__(self):
        self.queue = cycle(range(256))  # Create a cyclic iterator over numbers 0 to 255

    def pop(self):
        # Get the next number from the cyclic iterator
        return convert_to_hex(next(self.queue))

# Example usage:
queue = CircularByteQueue()

'''
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'141000F7', 'counter': '01 ', 'master': '01'})])
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'131000F7', 'counter': '01', 'master': '01'})])
'''


unk5 = '0000CF43'
unk6 = '00005244'
unk7 = '0000F042'

unk5 = '0000DC43'
unk6 = '00005244'
unk7 = '0000EE42'


port = 62038
packet = '''
self._model.dmetcp_queue.put(['B', packet_020E_shot_fired.packet_020E_shot_fired(network='tcp', map=self._model.game_state.map.map, weapon=self._model.game_state.player.weapon,src_player=self._model.game_state.player.player_id,time=self._model.game_state.player.time, object_id=-1, unk1='08', unk2='00000000', unk3='00000000', unk4='00000000', unk5='{unk5}', unk6='{unk6}', unk7='{unk7}')])
'''

def send_post_request():
    url = f'http://localhost:{port}/packet'  # Replace <port> with the actual port number


    while True:
        val = queue.pop()
        print(val)

        #unk7 = f'0000{val}42'
        new_packet = packet.format(unk5=unk5, unk6=unk6,unk7=unk7)

        data = {
            'packet': new_packet
        }

        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("Server response:")
                print(response.json())
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"Error: {e}")
        time.sleep(.1)

if __name__ == '__main__':
    send_post_request()