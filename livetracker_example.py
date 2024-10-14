# pip install git+https://github.com/Horizon-Private-Server/horizon-uya-bot.git
import os
import asyncio
import json

from livetrackerbackend import LiveTrackerBackend

loop = asyncio.new_event_loop()

# For prod
#tracker = LiveTrackerBackend(server_ip=os.getenv('SOCKET_IP'), log_level='INFO')

# For simulated
tracker = LiveTrackerBackend(server_ip=os.getenv('SOCKET_IP'), simulated=True, log_level='INFO')

tracker.start(loop)

while True:
    world_information = tracker.get_world_states()
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print("===========================================================================")
    print(json.dumps(world_information, indent=4))
    loop.run_until_complete(asyncio.sleep(1))
