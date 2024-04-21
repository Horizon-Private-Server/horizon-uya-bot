import requests



port = 52038
packet = '''
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'141000F7', 'counter': '01 ', 'master': '01'})])
self._model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype='p1_assign_to', timestamp=self._model.game_state.player.time, object_type='001000F7', data={'object_id':'131000F7', 'counter': '01', 'master': '01'})])
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