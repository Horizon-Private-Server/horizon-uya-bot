from medius.dme_packets import *
import asyncio


class prototype:
    def __init__(self, model, game_state):
        self._model = model
        self._game_state = game_state
        print(self._game_state)


    async def main_loop(self):
        while self._model.alive:


            packet_num = self._game_state.player.gen_packet_num()
            src_coord = [21219, 23327, 2167]

            # if self._udp_movement_packet_num % 2 == 0:
            #     coord = [35594, 17038, 12977]
            # else:
            #     coord = [35594, 17538, 12977]

            data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': 221, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': 221, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': 221, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': 221, 'buffer': '00', 'coord': src_coord, 'packet_num': packet_num, 'flush_type': 0, 'last': '7F7F7F7F7F7F7F7F', 'type': 'movement'}

            self._model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

            await asyncio.sleep(0.03)


    def __str__(self):
        return "prototype class"
