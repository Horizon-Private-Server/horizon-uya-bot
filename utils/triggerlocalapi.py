import requests



port = 10000



def send_post_request():
    url = f'http://localhost:{port}/packet'  # Replace <port> with the actual port number
    name = "test name"
    age = 150

    data = {
        'name': name,
        'age': age
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