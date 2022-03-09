import asyncio
import random
from scipy.spatial import distance

from constants.constants import ANIMATION_MAP
from medius.dme_packets import *
from utils.utils import *

class prototype:
    def __init__(self, model, game_state):
        self._model = model
        self.game_state = game_state

        self.game_state.player.coord = self.game_state.map.get_random_coord()
        self.game_state.player.x_angle = 127

        self._is_dead = False

        self.animation = None

        self.weapon = 'n60'

    async def main_loop(self):
        while self._model.alive:

            if self.weapon == 'n60':
                # Switch to flux
                self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])
                self.weapon = 'flux'

            if random.random() > .99:
                self._model.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=-1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])


            # update angle/coord
            if not self._is_dead:
                if self.game_state.player.movement_packet_num % 4 == 0:
                    new_coord = self.game_state.map.path(self.game_state.player.coord, self.game_state.players[0].coord, distance_to_move=30)
                    if new_coord[2] > self.game_state.player.coord[2]:
                        self.animation = 'jump'
                    elif new_coord != self.game_state.player.coord:
                        self.animation = 'forward'
                    else:
                        self.animation = None

                    self.game_state.player.coord = new_coord

            # Update camera angle
            if self.game_state.player.movement_packet_num % 20 == 0:
                self.game_state.player.x_angle = calculate_angle(self.game_state.player.coord, self.game_state.players[0].coord)





            # Update movement
            self.send_movement()

            await asyncio.sleep(0.03)

    def send_movement(self):
        packet_num = self.game_state.player.gen_packet_num()

        data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': self.game_state.player.x_angle, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': self.game_state.player.x_angle, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': self.game_state.player.x_angle, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': self.game_state.player.x_angle, 'buffer': '00', 'coord': self.game_state.player.coord, 'packet_num': packet_num, 'flush_type': 0, 'last': '7F7F7F7F7F7F7F7F', 'type': 'movement'}

        if self.animation != None:
            data['flush_type'] = 16
            data['animation'] = self.animation

        self._model.dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

        # God mode
        # self._model.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])
        #
        # self._model.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])



    def __str__(self):
        return "prototype class"
