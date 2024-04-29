import requests
import time
def hex_to_bytes(hex:str):
    return bytes(bytearray.fromhex(hex))
def bytes_to_int_little(data):
    return int.from_bytes(data, byteorder='little')
def hex_to_int_little(hex: str):
    return bytes_to_int_little(hex_to_bytes(hex))
'''
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'141000F7', 'counter': '01 ', 'master': '01'})])
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'131000F7', 'counter': '01', 'master': '01'})])
'''



# unk2 = "0000" # not needed for flux, needed for gravity
# local_x = 0
# unk3 = "0000" # not needed for flux, unknown for gravity
# local_y = 0
# unk4 = "0000" # not needed for flux
# local_z = 0

# unk5 = "0000"
# local_x_2 = 0
# unk6 = "0000"
# local_y_2 = 48532 # makes blitz hit center if 0
# unk7 = "0000"
# local_z_2 = 0 # last 2 bytes critical, first 2 bytes don't matter

# b1: local_x_2:7ABF unk6:E9B9  local_y_2:1ABE unk7:0D9B local_z_2:0E3E
# turret: local_x_2:F53D unk6:35A4  local_y_2:7B3F unk7:0D9B local_z_2:0E3E
# wall: local_x_2:3DBD unk6:513A  local_y_2:7DBF unk7:0D9B local_z_2:0E3E
# b2: local_x_2:7C3F unk6:B0C5  local_y_2:C8BD unk7:0D9B local_z_2:0E3E
# up: local_x_2:AEBE unk6:D0D9  local_y_2:E43C unk7:B28F local_z_2:703F

unk2 = "0000"
local_x = 0
unk3 = "0000"
local_y = 0
unk4 = "0000"
local_z = 0 

unk5 = "0000" 
local_x_2 = hex_to_int_little("00BF") 
unk6 ="0000"
local_y_2 = hex_to_int_little("00BE")  
unk7 = "0000"
local_z_2 = hex_to_int_little("003E") 

unk5 = "0000" 
local_x_2 = hex_to_int_little("7ABF") 
unk6 ="0000"
local_y_2 = hex_to_int_little("1EBE")  
unk7 = "0000"
local_z_2 = hex_to_int_little("0E3E") 

port = 62038
packet = f'''
self._model.dmetcp_queue.put(['B', packet_020E_shot_fired.packet_020E_shot_fired(network='tcp', map=self._model.game_state.map.map, weapon=self._model.game_state.player.weapon,src_player=self._model.game_state.player.player_id,time=self._model.game_state.player.time, object_id=-1, unk1='08', unk2='{unk2}', local_x={local_x}, unk3='{unk3}', local_y={local_y}, unk4='{unk4}', local_z={local_z}, unk5='{unk5}', local_x_2={local_x_2}, unk6='{unk6}', local_y_2={local_y_2}, unk7='{unk7}', local_z_2={local_z_2})])
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

if __name__ == '__main__':
    send_post_request()