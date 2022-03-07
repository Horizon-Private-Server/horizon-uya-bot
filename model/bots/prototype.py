import asyncio
import random
from scipy.spatial import distance

from medius.dme_packets import *
from utils.utils import *

class prototype:
    def __init__(self, model, game_state):
        self._model = model
        self.game_state = game_state

        if self.game_state.map.map == 'command_center':
            self.game_state.player.coord = [20707, 23601, 2152]
            self.game_state.player.x_angle = 127

    async def main_loop(self):
        while self._model.alive:
            #print(self.game_state)

            # update angle/coord
            if self.game_state.player.movement_packet_num % 5 == 0:

                self.game_state.player.coord = self.game_state.map.path(self.game_state.player.coord, self.game_state.players[0].coord)
            #print(self.game_state.players[0].coord)
            # grid = self.game_state.grid
            #
            # distances = distance.cdist(grid, [self.game_state.player.coord], 'euclidean')
            # # Get all coordinates within moveable distances
            # moveables = (distances < 40) & (distances > 20)
            # possible_coords = grid[moveables.flatten(),:]
            #
            # # Get point closest to enemy
            # distances = distance.cdist(possible_coords, [self.game_state.players[0].coord], 'euclidean')
            # min_idx = np.where(distances == np.amin(distances))[0][0]

            # Update camera angle
            if self.game_state.player.movement_packet_num % 20 == 0:
                self.game_state.player.x_angle = calculate_angle(self.game_state.player.coord, self.game_state.players[0].coord)

            # Update movement
            self.send_movement()

            await asyncio.sleep(0.03)

    def send_movement(self):
        packet_num = self.game_state.player.gen_packet_num()

        # if self._udp_movement_packet_num % 2 == 0:
        #     coord = [35594, 17038, 12977]
        # else:
        #     coord = [35594, 17538, 12977]

        data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': self.game_state.player.x_angle, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': self.game_state.player.x_angle, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': self.game_state.player.x_angle, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': self.game_state.player.x_angle, 'buffer': '00', 'coord': self.game_state.player.coord, 'packet_num': packet_num, 'flush_type': 0, 'last': '7F7F7F7F7F7F7F7F', 'type': 'movement'}

        self._model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

        # God mode
        # self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])
        #
        # self._model.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])



    def __str__(self):
        return "prototype class"
