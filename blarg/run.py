import asyncio
import websockets
async def read_websocket(ip):
    uri = f"ws://{ip}:8765"
    print("Connecting...")
    async with websockets.connect(uri,ping_interval=None) as websocket:
        print("Connected. Waiting for data.")
        while True:
            data = await websocket.recv()
            print(data)


ip = '216.146.25.143'
asyncio.new_event_loop().run_until_complete(read_websocket(ip))


