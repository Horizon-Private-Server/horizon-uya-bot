
import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

import asyncio

from medius.dme_packets import *
from medius.rt.clientappsingle import ClientAppSingleSerializer
from medius.rt.clientappbroadcast import ClientAppBroadcastSerializer

import queue
from utils.utils import *

class Model:
    def __init__(self, config, loop, tcp_conn, udp_conn):
        self._config = config

        self._account_id = self._config['account_id']
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
        self._dmetcp_queue = queue.Queue()
        self._dmeudp_queue = queue.Queue()

        self.time = 0

    def process(self, serialized: dict):
        '''
        PROCESS RT PACKETS
        '''
        #logger.debug(f"Processing: {serialized}")

        if serialized['packet'] == 'medius.rt.clientappsingle':
            for dme_packet in serialized['packets']:
                self.process_dme_packet(serialized['src_player'], dme_packet, serialized['protocol'])


    def process_dme_packet(self, src_player, dme_packet, protocol):
        '''
        PROCESS CLIENT APP SINGLE (DME)
        '''
        if protocol == 'TCP':
            self.process_dme_packet_tcp(src_player, dme_packet)
        elif protocol == 'UDP':
            pass
        else:
            logger.error("Unknown protocl: " + protocol)
            raise Exception()

    def process_dme_packet_tcp(self, src_player, dme_packet):
        '''
        PROCESS DME TCP DATA
        '''
        logger.debug(f"I | tcp; src:{src_player} {dme_packet}")

        if dme_packet.name == 'tcp_0016_player_connect_handshake':
            if dme_packet.data == '05000300010000000100000000000000':
                self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='03010300000000000000000000000000').to_bytes()])

        if dme_packet.name == 'tcp_0018_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0018_initial_sync.tcp_0018_initial_sync(src=self._dme_player_id).to_bytes()])
        if dme_packet.name == 'tcp_0010_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0010_initial_sync.tcp_0010_initial_sync(src=self._dme_player_id).to_bytes()])

        if dme_packet.name == 'tcp_0009_set_timer':
            self.time = dme_packet.time

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='04010300000000000000000000000000').to_bytes()])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=1, unk2='00000000000003000300000000001A000000', username=self._username, unk3='000300').to_bytes()])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update(unk1=1, unk2='00000000001003000300000000001A000000', username=self._username, unk3='000000').to_bytes()])

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake(data='04010300000000000200000000000000').to_bytes()])

            self._dmetcp_queue.put(['B', tcp_0210_player_joined.tcp_0210_player_joined(account_id=self._account_id, skin1=self._skin, skin2=self._skin, username=self._username, username2=self._username, rank=self._rank, clan_tag=self._clan_tag).to_bytes()])

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

                    if destination != 'B':
                        pkt = ClientAppSingleSerializer.build(destination, pkt)
                    else:
                        pkt = ClientAppBroadcastSerializer.build(pkt)

                    logger.debug(f"O | tcp; {pkt}")
                    self._tcp.queue(rtpacket_to_bytes(pkt))

            await asyncio.sleep(0.00001)


    def _dmeudpagg(self, serialized_packet):
        pass
