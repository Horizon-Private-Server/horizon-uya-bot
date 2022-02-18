
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
        self._skin = 1
        self._clan_tag = ''

        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn
        self._dme_player_id = self._tcp._player_id

        self._loop.create_task(self._dmetcpagg())
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
        logger.debug(f"Processing DME TCP packet (src:{src_player}): {dme_packet}")


        if dme_packet['packet'] == 'medius.dme_packets.tcp_0016_player_connect_handshake':
            if dme_packet['data'] == '05000300010000000100000000000000':
                self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake.build('03010300000000000000000000000000')])
            elif dme_packet['data'] == '05000300010080440100000000000000':
                pass

        if dme_packet['packet'] == 'medius.dme_packets.tcp_0018_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0018_initial_sync.tcp_0018_initial_sync.build()])
        if dme_packet['packet'] == 'medius.dme_packets.tcp_0010_initial_sync':
            self._dmetcp_queue.put([src_player, tcp_0010_initial_sync.tcp_0010_initial_sync.build(self._dme_player_id)])

        if dme_packet['packet'] == 'medius.dme_packets.tcp_0009_set_timer':
            self.time = dme_packet['time']

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake.build('04010300000000000000000000000000')])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update.build(1, '00000000000003000300000000001A000000', self._username, '000300')])

            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update.build(1, '00000000001003000300000000001A000000', self._username, '000000')])

            self._dmetcp_queue.put([src_player, tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake.build('04010300000000000200000000000000')])

            self._dmetcp_queue.put(['B', tcp_0210_player_joined.tcp_0210_player_joined.build(self._account_id, self._skin, self._username, self._clan_tag)])

            self._dmetcp_queue.put([src_player, tcp_0213_player_headset.tcp_0213_player_headset.build()])

            self._udp.queue(hex_to_bytes(f'032A0000000001{bytes_to_hex(int_to_bytes_little(4, self.time))}000000000001{bytes_to_hex(int_to_bytes_little(4, self.time))}010000000001{bytes_to_hex(int_to_bytes_little(4, self.time))}02000000'))

        if dme_packet['packet'] == 'medius.dme_packets.tcp_000F_playername_update':
            self._dmetcp_queue.put(['B', tcp_000F_playername_update.tcp_000F_playername_update.build(self.time, '000000000010030003000000000000000000', self._username, '001A00')])

    async def _dmetcpagg(self):
        '''
        This method is used to aggregate individual DME MGCL packets into a single packet
        in order to be queued. Ensure the total length < 500 bytes
        '''
        while True:
            size = self._dmetcp_queue.qsize()

            if size != 0:
                all_packets = [self._dmetcp_queue.get() for _ in range(size)]
                all_destinations = set([packet_combo[0] for packet_combo in all_packets])

                for destination in all_destinations:
                    this_dest_packets = [dme_packet_to_bytes(pkt[1]) for pkt in all_packets if pkt[0] == destination]

                    final_data = b'' ## TODO: Make sure this is < 500 length
                    for pkt in this_dest_packets:
                        final_data += pkt

                    # Before we queue it, we have to wrap it in a CLIENT_APP_SINGLE/BROADCAST
                    if destination != 'B':
                        pkt = ClientAppSingleSerializer.build(destination, final_data)
                    else:
                        pkt = ClientAppBroadcastSerializer.build(final_data)

                    final_pkt = rtpacket_to_bytes(pkt)

                    self._tcp.queue(final_pkt)

            await asyncio.sleep(0.00001)


    def _dmeudpagg(self, serialized_packet):
        pass
