import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

import sys

import asyncio

from medius.dme_packets import *
from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer

import queue
from utils.utils import *

class Model:
    def __init__(self, config, loop, tcp_conn, udp_conn):
        self.alive = True
        self._config = config

        self._account_id = self._config['account_id']
        self._team = self._config['team']
        self._username = self._config['username']
        self._skin = self._config['skin']
        if self._config['bolt'] == 1:
            self._rank = '00C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF43'
        elif self._config['bolt'] == 2:
            self._rank = '00C0A84400C0A84400C0A84400C0A84400808443008084430080844300808443'
        elif self._config['bolt'] == 3:
            self._rank = '00C0A84400C0A84400C0A84400C0A84400000000000000000000000000000000'
        elif self._config['bolt'] == 4:
            self._rank = 'C8C8D444C8C8D444C8C8D444C8C8D44400808943008089430080894300808943'

        self._clan_tag = self._config['clan_tag']

        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn
        self._dme_player_id = self._tcp._player_id

        self._loop.create_task(self._tcp_flusher())
        self._loop.create_task(self._udp_flusher())
        self._dmetcp_queue = queue.Queue()
        self._dmeudp_queue = queue.Queue()

        self._udp_movement_packet_num = 0

        self.time = 0

    def process(self, serialized: dict):
        '''
        PROCESS RT PACKETS
        '''
        #logger.debug(f"Processing: {serialized}")

        if serialized['packet'] == 'medius.rt.clientappsingle':
            for dme_packet in serialized['packets']:
                self.process_dme_packet(serialized['src_player'], dme_packet, serialized['protocol'])
        if serialized['packet'] == 'medius.rt.serverdisconnectnotify':
            if serialized['dme_player_id'] == 0:
                logger.info("Host has left! Exiting ...")
                self.alive = False


    def process_dme_packet(self, src_player, dme_packet, protocol):
        '''
        PROCESS DME TCP DATA
        '''
        logger.debug(f"I | tcp; src:{src_player} {dme_packet}")

        if dme_packet.name == 'tcp_0016_player_connect_handshake':
            if dme_packet.data == '05000300010000000100000000000000':
                self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='03010300000000000000000000000000')])

        if dme_packet.name == 'tcp_0018_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0018_initial_sync.tcp_0018_initial_sync(src=self._dme_player_id)])
        if dme_packet.name == 'tcp_0010_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0010_initial_sync.tcp_0010_initial_sync(src=self._dme_player_id)])

        if dme_packet.name == 'tcp_0009_set_timer':
            self.time = dme_packet.time

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='04010300000000000000000000000000')])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=1, unk2='00000000000003000300000000001A000000', username=self._username, unk3='000300')])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=1, unk2='00000000001003000300000000001A000000', username=self._username, unk3='000000')])

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='04010300000000000200000000000000')])

            self._dmetcp_queue.put(['B', tcp_0210_player_joined.tcp_0210_player_joined(account_id=self._account_id, skin1=self._skin, skin2=self._skin, username=self._username, username2=self._username, rank=self._rank, clan_tag=self._clan_tag)])

            self._dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self._team,skin='robo',username=self._username, ready='ready')])

        if dme_packet.name == 'tcp_0211_player_lobby_state_change' and src_player == 0 and dme_packet.ready == 'change team request':
            self._team = self._get_new_team(self._team)
            self._dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self._team,skin='robo',username=self._username, ready='ready')])

        if dme_packet.name == 'tcp_0004_tnw' and dme_packet.tnw_type == 'tNW_PlayerData':
            self._dmetcp_queue.put(['B', tcp_0004_tnw.tcp_0004_tnw(tnw_type='tNW_PlayerData', data={'unk1': '0100000002D301000300C6BF6C2A3C0000000000', 'unk2':'4119700F44BF23764345A44843000000000000000000000000D8EA14405B2A3C00000000000000000000000000000000000000000050C3000001000010000000000000000000000000D8EA14405B2A3C0050C3000001000010000000000000000000007041000000000000000000000000000000000000010000000100000001000000010000000100000000000000000000003200000032000000320000000000'})])
            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk2='000000000300030003000000000070410000', username=self._username, unk3='000000')])
            self._dmetcp_queue.put([0, tcp_0004_tnw.tcp_0004_tnw(tnw_type='tNW_PlayerData', data={'unk1': '0100000002D301000300C6BF6C2A3C0000000000', 'unk2':'4119700F44BF23764345A44843000000000000000000000000D8EA14405B2A3C00000000000000000000000000000000000000000050C3000001000010000000000000000000000000D8EA14405B2A3C0050C3000001000010000000000000000000007041000000000000000000000000000000000000010000000100000001000000010000000100000000000000000000003200000032000000320000000000'})])

            self._loop.create_task(self.movement_update())

        if dme_packet.name == 'udp_0001_timer_update':
            self.time = dme_packet.time
            self._dmeudp_queue.put([0, udp_0001_timer_update.udp_0001_timer_update(time=self.time, unk1=dme_packet.unk1)])


        if dme_packet.name == 'tcp_0012_player_left':
            if src_player == 0:
                logger.info("Host has left! Exiting ...")
                self.alive = False

    async def movement_update(self):
        while True:

            packet_num = self._udp_movement_packet_num
            self._udp_movement_packet_num += 1
            if self._udp_movement_packet_num == 256:
                self._udp_movement_packet_num = 0

            if self._udp_movement_packet_num < 100:
                coord = [35594, 17038, 12977]
            else:
                coord = [35594, 17538, 12977]


            data = {'r1': '7F', 'cam1_y': 127, 'cam1_x': 221, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 127, 'cam2_x': 221, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 127, 'cam3_x': 221, 'v_drv': '00', 'r4': '7F', 'cam4_y': 127, 'cam4_x': 221, 'buffer': '00', 'coord': coord, 'packet_num': packet_num, 'flush_type': 0, 'last': '7F7F7F7F7F7F7F7F', 'type': 'movement'}
            self._dmeudp_queue.put(['B', udp_0209_movement_update.udp_0209_movement_update(data=data)])

            await asyncio.sleep(0.15)

    async def _tcp_flusher(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while True:
            size = self._dmetcp_queue.qsize()

            if size != 0:
                for _ in range(size):
                    destination, pkt = self._dmetcp_queue.get()
                    # pkt = dme_packet_to_bytes(pkt)
                    logger.debug(f"O | tcp; dst:{destination} {pkt}")

                    if destination != 'B':
                        pkt = ClientAppSingleSerializer.build(destination, pkt.to_bytes())
                    else:
                        pkt = ClientAppBroadcastSerializer.build(pkt.to_bytes())

                    self._tcp.queue(rtpacket_to_bytes(pkt))

            await asyncio.sleep(0.00001)


    async def _udp_flusher(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while True:
            size = self._dmeudp_queue.qsize()

            if size != 0:
                for _ in range(size):
                    destination, pkt = self._dmeudp_queue.get()
                    logger.debug(f"O | udp; dst:{destination} {pkt}")

                    if destination != 'B':
                        pkt = ClientAppSingleSerializer.build(destination, pkt.to_bytes())
                    else:
                        pkt = ClientAppBroadcastSerializer.build(pkt.to_bytes())

                    self._udp.queue(rtpacket_to_bytes(pkt))

            await asyncio.sleep(0.00001)

    def _get_new_team(self, team): # TODO: incorporate gamemode
        if team == 'blue':
            return 'red'
        if team == 'red':
            return 'green'
        if team == 'green':
            return 'orange'
        if team == 'orange':
            return 'yellow'
        if team == 'yellow':
            return 'purple'
        if team == 'purple':
            return 'aqua'
        if team == 'aqua':
            return 'pink'
        if team == 'pink':
            return 'blue'
        return 'blue'
