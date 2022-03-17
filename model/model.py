import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.WARNING)

import sys

import asyncio

from medius.dme_packets import *
from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer

import queue
from utils.utils import *

from model.player_state import PlayerState
from model.game_state import GameState
from model.bots import *


class Model:
    def __init__(self, config, loop, tcp_conn, udp_conn):
        self.alive = True
        self._config = config

        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn

        player = PlayerState(self._tcp._player_id, config['account_id'], config['team'], username=config['username'], skin=config['skin'], clan_tag=config['clan_tag'], rank=config['bolt'])
        self.game_state = GameState(self._config['gameinfo'], player, self._config)
        self.bot = eval(f"{config['bot_class']}.{config['bot_class']}(self, self.game_state)")

        self._loop.create_task(self._tcp_flusher())
        self._loop.create_task(self._udp_flusher())
        self.dmetcp_queue = queue.Queue()
        self.dmeudp_queue = queue.Queue()


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
        This method is to process packets that are not handled with in-game logic, but rather handling the connection handshake, and other boring things.
        '''
        logger.debug(f"I | {protocol}; src:{src_player} {dme_packet}")

        if dme_packet.name == 'tcp_0016_player_connect_handshake' and dme_packet.subtype == 'host_initial_handshake':
            if dme_packet.unk1 == '03000100000001':
                #self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='03010300000000000000000000000000')])
                self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(subtype='player_initial_handshake', src_player=self.game_state.player.player_id, unk1='03000000000000')])

        if dme_packet.name == 'tcp_0018_initial_sync':
            self.dmetcp_queue.put([src_player, tcp_0018_initial_sync.tcp_0018_initial_sync(src=self.game_state.player.player_id)])
        if dme_packet.name == 'tcp_0010_initial_sync':
            self.dmetcp_queue.put([src_player, tcp_0010_initial_sync.tcp_0010_initial_sync(src=self.game_state.player.player_id)])

        if dme_packet.name == 'tcp_0009_set_timer' and src_player == 0:
            self.game_state.player.time = dme_packet.time

            self.dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=self.game_state.player.player_id, unk2='00000000000003000300000000001A000000', username=self.game_state.player.username, unk3='000300')])
            self.dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=self.game_state.player.player_id, unk2='00000000001003000300000000001A000000', username=self.game_state.player.username, unk3='000000')])


            self.dmetcp_queue.put(['B', tcp_0210_player_joined.tcp_0210_player_joined(account_id=self.game_state.player.account_id, skin1=self.game_state.player.skin, skin2=self.game_state.player.skin, username=self.game_state.player.username, username2=self.game_state.player.username, rank=self.game_state.player.rank, clan_tag=self.game_state.player.clan_tag)])

            self.dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self.game_state.player.team,skin=self.game_state.player.skin,username=self.game_state.player.username, ready='ready')])

        if dme_packet.name == 'tcp_0211_player_lobby_state_change' and src_player == 0 and dme_packet.ready == 'change team request':
            new_team = self.game_state.player.change_teams()
            self.dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self.game_state.player.team,skin=self.game_state.player.skin,username=self.game_state.player.username, ready='ready')])

        if dme_packet.name == 'tcp_000D_game_started':
            self._loop.create_task(self.send_player_data())
            self.game_state.state = 'active'

        if dme_packet.name == 'udp_0001_timer_update':
            self.game_state.player.time = dme_packet.time
            self.dmeudp_queue.put([0, udp_0001_timer_update.udp_0001_timer_update(time=self.game_state.player.time, unk1=dme_packet.unk1)])
            self.game_state.time_update(src_player, dme_packet.time)


        if dme_packet.name == 'tcp_0012_player_left':
            if src_player == 0:
                logger.info("Host has left! Exiting ...")
                self.alive = False

        if dme_packet.name == 'tcp_0003_broadcast_lobby_state' and src_player == 0 and dme_packet.data['num_messages'] == 1 and dme_packet.data['msg0']['type'] == 'timer_update':
            self.game_state.player.time = dme_packet.data['msg0']['time']
            self.dmetcp_queue.put([0, tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'timer_update', 'time': self.game_state.player.time}})])

        if dme_packet.name == 'tcp_0004_tnw' and dme_packet.tnw_type == 'tNW_PlayerData':
            self.game_state.tnw_playerdata_update(src_player, dme_packet.data)


        if dme_packet.name == 'udp_0209_movement_update':
            self.game_state.movement_update(src_player, dme_packet.data)



        if dme_packet.name in ['udp_020E_shot_fired']:
            self.bot.process_shot_fired(src_player, dme_packet)

            ## Examples
        #     self.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])
        #
        #   self.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])

            #self._tcp.queue(rtpacket_to_bytes(ClientAppBroadcastSerializer.build(hex_to_bytes('0204003901030E00000001000000'))))

            # self.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_changed', 'weapon_changed_to': 'flux'}})])

            # self.dmeudp_queue.put(['B', udp_020E_shot_fired.udp_020E_shot_fired(weapon_type='03004108',time=self.game_state.player.time, moby_id=1, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0)])

            # self.dmetcp_queue.put(['B', tcp_0204_player_killed.tcp_0204_player_killed(killer_id=0, killed_id=1, weapon='grav')])
            # self.dmetcp_queue.put(['B', tcp_0204_player_killed.tcp_0204_player_killed(killer_id=0, killed_id=1, weapon='blitz')])

    async def send_player_data(self):
        # It takes 13 seconds to load from game start into actual game
        await asyncio.sleep(14)


        # Command Center
        # unk1 = '01000000026E010003000000C173250000000000'
        # unk2 = '0066809443620B8B4309BA48430000000000000000000000000F73E83F'
        # unk3 = '0000000000000000000000000000000000000000'
        # unk4 = '010000100000000000000000000000000F73E83F'
        # unk5 = '00000100001000000000'
        # unk6 = '00000000007041000000000000000000000000000000000000010000000100000000000000010000000100000000000000000000003200000064000000320000000100'

        # Aquatos Sewers
        unk1='0100000002D301000300C6BF8EE7000000000000'
        unk2='4116E1C7430A7EBA43B2446B44000000000000000000000000DB0FC9BF'
        unk3='0000000000000000000000000000000000000000'
        unk4='01000010000000000000000000000000DB0FC9BF'
        unk5='00000100001000000000'
        unk6='00000000007041000000000000000000000000000000000000010000000100000000000000010000000100000000000000000000003200000064000000320000000100'

        self.dmetcp_queue.put(['B', tcp_0004_tnw.tcp_0004_tnw(tnw_type='tNW_PlayerData', data={'unk1': unk1, 'unk2':unk2, 'player_start_time_1': self.game_state.player.time, 'player_start_time_2': self.game_state.player.time, 'unk3': unk3, 'account_id_1': self.game_state.player.account_id, 'account_id_2': self.game_state.player.account_id, 'team':self.game_state.player.team, 'unk4': unk4, 'unk5': unk5, 'unk6':unk6})])

        ####
        self.dmetcp_queue.put(['B', tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(unk1='00000000', team='blue', skin='ratchet', ready='unk, player in-game ready(?)', username='', unk2='0000000000000000000000')])

        self._loop.create_task(self.bot.main_loop())



    async def _tcp_flusher(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while True:
            try:
                size = self.dmetcp_queue.qsize()
                if size != 0:
                    for _ in range(size):
                        destination, pkt = self.dmetcp_queue.get()
                        logger.debug(f"O | tcp; dst:{destination} {pkt}")

                        if destination != 'B':
                            pkt = ClientAppSingleSerializer.build(destination, pkt.to_bytes())
                        else:
                            pkt = ClientAppBroadcastSerializer.build(pkt.to_bytes())

                        self._tcp.queue(rtpacket_to_bytes(pkt))

                await asyncio.sleep(0.00001)
            except:
                logger.exception("TCP FLUSHER ERROR")
                self.alive = False
                break


    async def _udp_flusher(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while True:
            try:
                size = self.dmeudp_queue.qsize()

                if size != 0:
                    for _ in range(size):
                        destination, pkt = self.dmeudp_queue.get()
                        logger.debug(f"O | udp; dst:{destination} {pkt}")

                        if destination != 'B':
                            pkt = ClientAppSingleSerializer.build(destination, pkt.to_bytes())
                        else:
                            pkt = ClientAppBroadcastSerializer.build(pkt.to_bytes())

                        self._udp.queue(rtpacket_to_bytes(pkt))

                await asyncio.sleep(0.00001)
            except:
                logger.exception("UDP FLUSHER ERROR")
                self.alive = False
                break
