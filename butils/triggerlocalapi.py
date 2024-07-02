import requests
import time
def hex_to_bytes(hex:str):
    return bytes(bytearray.fromhex(hex))
def bytes_to_int_little(data):
    return int.from_bytes(data, byteorder='little')
def hex_to_int_little(hex: str):
    return bytes_to_int_little(hex_to_bytes(hex))

def int_to_bytes_little(bytelength, data, signed=False):
    return data.to_bytes(bytelength, 'little', signed=signed)
def bytes_to_hex(data:bytes):
    return data.hex().upper()
port = 10883


counter = 0

while True:
    '''
    61D1
    D543
    ADD9
    5344
    3F1B
    E942

    00000000

    p0_flag_drop timestamp:119349 object_type:131000F7 data:
    '''
    if counter == 255:
        counter = 0
    else:
        counter +=1 

    val = bytes_to_hex(int_to_bytes_little(1, counter))

    # unk1 = int_to_bytes_little(1138086241)
    # unk2 = int_to_bytes_little()
    # unk3 = int_to_bytes_little()
    unk1 = "61" + val
    unk2 = "D543"
    unk3 = "ADD9"
    unk4 = "5344"
    unk5 = "3F1B"
    unk6 = "E942"
    unk = unk1+unk2+unk3+unk4+unk5+unk6



    packet = f'''
    self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p1_object_update', object_type='131000F7',timestamp=self._model.game_state.player.time,data={{'object_update_unk': '01000000'}})])
    '''

    packet = f'''
    self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p1_flag_drop', object_type='131000F7',timestamp=self._model.game_state.player.time,data={{'flag_drop_unk': '{unk}'}})])
    '''



    def send_post_request():
        url = f'http://localhost:{port}/packet'  # Replace <port> with the actual port number

        data = {
            'packet': packet
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

    time.sleep(.01)

    if __name__ == '__main__':
        send_post_request()