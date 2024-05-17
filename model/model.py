import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.INFO)

import sys

import asyncio
from datetime import datetime

from medius.dme_packets import *
from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer

import queue
from butils.utils import *

from model.player_state import PlayerState
from model.game_state import GameState
from model.bots import *

from constants.constants import parse_object_id, MAIN_BOT_LOOP_TIMER

from medius.serializer import UdpSerializer
from medius.serializer import TcpSerializer

class Model:
    def __init__(self, loop, network_manager, gameinfo, bot_class, account_id, player_id, team, username, skin, clan_tag, bolt):
        logger.info("Initialzing model ...")
        logger.info(f"GAME INFO: {gameinfo}")
        self.alive = True
        username = 'i aM a nOOb'
        self.loop = loop

        self._network = network_manager
        self.dmetcp_queue = queue.Queue()
        self.dmeudp_queue = queue.Queue()

        self._seen_first_player_movement = False

        player = PlayerState(player_id, account_id, team, username=username, skin=skin, clan_tag=clan_tag, rank=bolt)
        self.game_state = GameState(self, gameinfo, player)

        self.bot = eval(f"{bot_class}.{bot_class}(self, self.game_state)")

        self.loop.create_task(self._tcp_flusher())
        self.loop.create_task(self._udp_flusher())
        self.loop.create_task(self._tcp_reader())
        self.loop.create_task(self._udp_reader())

    async def _tcp_reader(self):
        while self.alive:
            if self._network._dmetcp.qsize() != 0:
                packet = self._network._dmetcp.dequeue()
                try:
                    serialized = TcpSerializer[packet[0]]['serializer'].serialize(packet)
                    self.process(serialized)
                except:
                    logger.exception(f"Error processing DME TCP packet: {packet}")
            await asyncio.sleep(0.0001)

    async def _udp_reader(self):
        while self.alive:
            if self._network._dmeudp.qsize() != 0:
                packet = self._network._dmeudp.dequeue()
                try:
                    serialized = UdpSerializer[packet[0]]['serializer'].serialize(packet)
                    self.process(serialized)
                except:
                    logger.exception(f"Error processing DME UDP packet: {packet}")
            await asyncio.sleep(0.0001)


    def process(self, serialized: dict):
        '''
        PROCESS RT PACKETS
        '''
        logger.debug(f"Processing: {serialized}")

        if serialized['packet'] == 'medius.rt.clientappsingle':
            for dme_packet in serialized['packets']:
                self.process_dme_packet(serialized['src_player'], dme_packet, serialized['protocol'])
        if serialized['packet'] == 'medius.rt.serverdisconnectnotify':
            if serialized['dme_player_id'] == 0:
                logger.info("Host has left! Exiting ...")
                self.alive = False
            else:
                self.game_state.player_left(serialized['dme_player_id'])


    def process_dme_packet(self, src_player, dme_packet, protocol):
        '''
        This method is to process packets that are not handled with in-game logic, but rather handling the connection handshake, and other boring things.
        '''
        logger.debug(f"I | {protocol}; src:{src_player} {dme_packet}")

        if dme_packet.name == 'tcp_000F_playername_update' and dme_packet.unk3 == '001A00':
            self.dmetcp_queue.put([0, tcp_000F_playername_update.tcp_000F_playername_update(unk1=32958977, unk2='00000000000003000300000000001A000000', username=self.game_state.player.username, unk3='001A00')])

        if dme_packet.name == 'tcp_0016_player_connect_handshake' and dme_packet.subtype == 'host_initial_handshake':
            if dme_packet.unk1 == '03000100000001':
                #self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='03010300000000000000000000000000')])
                self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(subtype='player_initial_handshake', src_player=self.game_state.player.player_id, unk1='03000000000000')])
            elif dme_packet.unk1 == '03000100804401':
                self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(subtype='handshake', src_player=self.game_state.player.player_id, unk1='03000000000000')])
                self.dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(subtype='handshake', src_player=self.game_state.player.player_id, unk1='03000000000002')])

        if dme_packet.name == 'tcp_0018_initial_sync':
            self.loop.create_task(self.send_tcp_0018(src_player))

        if dme_packet.name == 'tcp_0010_initial_sync':
            self.dmetcp_queue.put([src_player, tcp_0010_initial_sync.tcp_0010_initial_sync(src=self.game_state.player.player_id)])

        if dme_packet.name == 'tcp_0009_set_timer' and src_player == 0:
            self.game_state.player.time = dme_packet.time

            self.dmetcp_queue.put([0, tcp_000F_playername_update.tcp_000F_playername_update(unk1=self.game_state.player.player_id, unk2='00000000000003000300000000001A000000', username=self.game_state.player.username, unk3='000300')])
            self.dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=self.game_state.player.player_id, unk2='00000000001003000300000000001A000000', username=self.game_state.player.username, unk3='000000')])
            self.dmetcp_queue.put(['B', tcp_0210_player_joined.tcp_0210_player_joined(account_id=self.game_state.player.account_id, skin1=self.game_state.player.skin, skin2=self.game_state.player.skin, username=self.game_state.player.username, username2=self.game_state.player.username, rank=self.game_state.player.rank, clan_tag=self.game_state.player.clan_tag)])
            self.dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self.game_state.player.team,skin=self.game_state.player.skin,username=self.game_state.player.username, ready='ready', clan_tag=self.game_state.player.clan_tag)])

        if dme_packet.name == 'tcp_0211_player_lobby_state_change' and src_player == 0 and dme_packet.ready == 'change team request':
            self.game_state.player.change_teams(self.game_state.game_mode)
            self.dmetcp_queue.put([0, tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(team=self.game_state.player.team,skin=self.game_state.player.skin,username=self.game_state.player.username, ready='ready', clan_tag=self.game_state.player.clan_tag)])

        if dme_packet.name == 'tcp_000D_game_started':
            self.game_state.start()
            self.loop.create_task(self.send_player_data())
            self.loop.create_task(self.timer_update())
            self.game_state.state = 'active'

        if dme_packet.name == 'udp_0001_timer_update':
            if src_player == 0:
                self.game_state.player.time = dme_packet.time
            self.game_state.time_update(src_player, dme_packet.time)


        if dme_packet.name == 'tcp_0012_player_left':
            if src_player == 0:
                logger.info("Host has left! Exiting ...")
                self.alive = False


        if dme_packet.name == 'tcp_0003_broadcast_lobby_state':
            msgs = [key for key in dme_packet.data.keys() if key[0:3] == 'msg']

            for msg in msgs:
                if src_player == 0 and dme_packet.data['src'] == -1 and dme_packet.data[msg]['type'] == 'ready/unready' and dme_packet.data[msg][f'p{self.game_state.player.player_id}'] == 'kicked':
                    self.alive = False
                if dme_packet.data[msg]['type'] == 'timer_update':
                    self.game_state.time_update(src_player, dme_packet.data[msg]['time'])
                    if src_player == 0:
                        self.game_state.player.time = dme_packet.data[msg]['time']

                if dme_packet.data[msg]['type'] == 'health_update':
                    self.game_state.players[src_player].health = dme_packet.data[msg]['health']
                    if self.game_state.players[src_player].health == 0:
                        self.game_state.players[src_player].is_dead = True
                    else:
                        self.game_state.players[src_player].is_dead = False

                if dme_packet.data[msg]['type'] == 'weapon_upgraded':
                    self.game_state.players[src_player].set_weapon_upgrades(dme_packet.data[msg])


        if dme_packet.name == 'tcp_020A_player_respawned':
            self.game_state.players[src_player].respawn()

        if dme_packet.name == 'tcp_0004_tnw' and dme_packet.tnw_type == 'tNW_PlayerData':
            self.game_state.tnw_playerdata_update(src_player, dme_packet.data)

        if dme_packet.name == 'tcp_0004_tnw' and dme_packet.tnw_type == 'tNW_GameSetting':
            self.game_state.tnw_gamesetting_update(src_player, dme_packet.data)

        if dme_packet.name == 'udp_0209_movement_update':
            self.game_state.movement_update(src_player, dme_packet.data)

        if dme_packet.name in ['packet_020E_shot_fired']:
            self.bot.process_shot_fired(src_player, dme_packet)

        if dme_packet.name == 'udp_0001_timer_update' and dme_packet.unk1 == '00010000':
            self.dmeudp_queue.put([src_player, udp_0001_timer_update.udp_0001_timer_update(time=self.game_state.player.time, unk1="0000FFFF")])
            self.dmeudp_queue.put([src_player, udp_0001_timer_update.udp_0001_timer_update(time=self.game_state.player.time, unk1="00010000")])

        if dme_packet.name == 'tcp_020C_info':
            self.game_state.object_manager.object_update(src_player, dme_packet)



    async def send_tcp_0018(self, src_player):
        await asyncio.sleep(3)
        self.dmetcp_queue.put([src_player, tcp_0018_initial_sync.tcp_0018_initial_sync(src=self.game_state.player.player_id)])

    async def send_player_data(self):
        # It takes 13 seconds to load from game start into actual game
        # await asyncio.sleep(18)

        # Aquatos Sewers
        test_map = {
            0: '01',
            1: '03',
            2: '06',
            3: '09',
            4: '0C',
            5: '0F',
            6: '12',
            7: '15'
        }

        if self.game_state.map.map == 'bakisi_isles':
            map_specific_1 = '00C6BF09AA780100000000'
            unk2='41C51302446893AC4332E347430000000000000000000000005E4D0740'
            map_specific_2 = 'DB0FC9BF'
        elif self.game_state.map.map == 'metropolis':
            map_specific_1 = '00C6BF60B8000000000000'
            unk2='41EF9A37445643694399B7A7430000000000000000000000001514C93F'
            map_specific_2 = '1514C93F'
        elif self.game_state.map.map == 'aquatos_sewers':
            map_specific_1 = '00C6BF8EE7000000000000'
            unk2='4116E1C7430A7EBA43B2446B44000000000000000000000000DB0FC9BF'
            map_specific_2 = 'DB0FC9BF'
        else:
            # Marcadia_Palace
            map_specific_1 = '00C6BF4CD8340000000000'
            unk2='41A8E9DF4380735D4436F0E742000000000000000000000000E9F18ABF'
            map_specific_2 = 'E9F18ABF'

        unk1=f'0{self.game_state.player.player_id}00000002D30{self.game_state.player.player_id}00{test_map[self.game_state.player.player_id]}{map_specific_1}'
        unk3='0000000000000000000000000000000000000000'
        unk4=f'010000{self.game_state.player.player_id}0000000000000000000000000{map_specific_2}'
        unk5=f'0000010000{self.game_state.player.player_id}000000000'
        unk6=f'000000000070410000000000000000000000000000000000000{self.game_state.player.player_id}0000000100000000000000010000000100000000000000000000003200000064000000320000000100'

        self.dmetcp_queue.put(['B', tcp_0004_tnw.tcp_0004_tnw(tnw_type='tNW_PlayerData', data={'unk1': unk1, 'unk2':unk2, 'player_start_time_1': self.game_state.player.time, 'player_start_time_2': self.game_state.player.time, 'unk3': unk3, 'account_id_1': self.game_state.player.account_id, 'account_id_2': self.game_state.player.account_id, 'team':self.game_state.player.team, 'unk4': unk4, 'unk5': unk5, 'unk6':unk6})])

        self.dmetcp_queue.put([0, tcp_000F_playername_update.tcp_000F_playername_update(unk1=1, unk2='000000000300030003000000000070410000', username=self.game_state.player.username, unk3='000000')])

        self.dmetcp_queue.put(['B', tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change(unk1='00000000', team='blue', skin='ratchet', ready='unk, player in-game ready(?)', username='', clan_tag='    ')])

        self.dmetcp_queue.put(['B', tcp_0205_unk.tcp_0205_unk()])

        # Charge boots
        self.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 2, 'src': self.game_state.player.player_id, 'msg0': {'type': 'weapon_update_0A'}, 'msg1': {'type': 'weapon_update_0C'}})])

        self.loop.create_task(self.wait_until_game_start())


    async def wait_until_game_start(self):
        # Wait until we have movement data
        while self.alive and self.game_state.players[0].coord == [0,0,0]:
            await asyncio.sleep(.1)

        # Reset Object Masters
        self.game_state.object_manager.reset_all_masters()

        self.loop.create_task(self.bot.main_loop())


    async def timer_update(self):
        while self.alive:
            try:
                self.dmetcp_queue.put(['B', tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state(data={'num_messages': 1, 'src': self.game_state.player.player_id, 'msg0': {'type': '09_timer_update', 'time': self.game_state.player.time}})])
                await asyncio.sleep(1)
            except:
                logger.exception("TIMER UPDATE ERROR")
                self.alive = False
                break

    def get_closest_enemy_player(self):
        players = [p for p in self.game_state.players.values() if p.team != self.game_state.player.team and p.is_dead == False]

        if players == []:
            players = [p for p in self.game_state.players.values() if p.team != self.game_state.player.team]

        if players == []:
            players = [p for p in self.game_state.players.values()]

        idx = find_closest_node_from_list(self.game_state.player.coord, [p.coord for p in players])
        closest_player = players[idx]

        return closest_player


    async def _tcp_flusher(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while self.alive:
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
                        self._network._dmetcp.queue(rtpacket_to_bytes(pkt))

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
        while self.alive:
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

                        self._network._dmeudp.queue(rtpacket_to_bytes(pkt))

                await asyncio.sleep(0.00001)
            except:
                logger.exception("UDP FLUSHER ERROR")
                self.alive = False
                break


    async def kill(self):
        logger.info(f"Killing Model ...")
        self.alive = False                        
        logger.info(f"Killed.")
