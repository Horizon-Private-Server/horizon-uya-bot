# How to run Blarg to listen to packets on the prod or test UYA server

Default config:
```
{
        "prod": "",
        "test": "",
        "logger": "INFO",
        "filter": "",
        "warn_on_unknown": "False",
        "log_serialized": "True",
        "fail_on_error": "False",
        "src_filter": [],
        "exclude": []
}
```
Explanation:
```
prod -> prod server IP. You specify if you want to listen to prod or test with the `--target` flag when running `python blarg.py`
test -> testprod server IP. You specify if you want to listen to prod or test 
logger -> what log level to use. the logfile written in `logs/` will always be set to DEBUG. this only affects the console output. if INFO, and log_serialized=True, then it will print the structured output. DBEUG will print the raw packet hex byte data as well as who sent it and to whom it was sent. -1 means it is a broadcast message sent to everyone in the lobby from that person
filter -> This is a specific packet you want to monitor. E.g. "0209" means the terminal output will only output movement packet data and pad input since 0209 is the ID
warn_on_unknown -> If blarg should warn if it receives an unknown packet that we have not tried yet to deserialize
log_serialized -> If True, it will log the serialized data
fail_on_error -> if true, will stop the program if we error on trying to deserialize a packet
src_filter -> This is a list of src player IDs this way you can see in the terminal only 1 person's packets for easier debugging
exclude -> Packet IDs to exclude since the terminal can be a lot of packets at once and some are not needed
```

Example `DEBUG` logging line:
```
2025-07-16 12:02:50,831 blarg | DEBUG | [{"type": "udp", "dme_world_id": 0, "src": 0, "dst": -1, "data": "02097F7FDD007F7FDD007F7FDD007F7FDD00638C7A3D85321D007F7F7F7F7F7F7F7F"}]
```
The type is udp/tcp. dme_world_id is the game world ID. Src is the person's ID who SENT the packet, and dst is the destination ID that the src player wanted to send the packet to. DST=-1 means its a broadcast message and this will get sent to everyone individually.


Example `INFO` logging line (serialized from the above hex data):
```
2025-07-16 12:02:50,832 blarg | INFO | 0 -> -1 | udp_0209_movement_update; data:{'r1': '7F', 'cam1_y': 127, 'cam1_x': 221, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': 221, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': 221, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': 221, 'buffer': '00', 'coord': [35939, 15738, 12933], 'packet_num': 29, 'flush_type': 0, 'left_joystick_x': 89, 'left_joystick_y': 89, 'left_joystick_repeats': '7F7F7F7F7F7F', 'type': 'movement'}
```
You can see that the data has been broken down into different data structures that have been reverse engineered.
