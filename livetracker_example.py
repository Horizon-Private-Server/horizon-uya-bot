
# pip install git+https://github.com/Horizon-Private-Server/horizon-uya-bot.git
import os
import asyncio

from livetrackerbackend import LiveTrackerBackend

loop = asyncio.new_event_loop()
tracker = LiveTrackerBackend(loop, server_ip=os.getenv('SOCKET_IP'), log_level='INFO')

while True:
    world_information = tracker.get_world_states()
    print(world_information)
    loop.run_until_complete(asyncio.sleep(1))