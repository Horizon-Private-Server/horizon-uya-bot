
import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

import asyncio

from medius.dme_packets import *
from medius.rt.clientappsingle import ClientAppSingleSerializer

import queue

from utils.utils import dme_packet_to_bytes, rtpacket_to_bytes

class Model:
    def __init__(self, loop, tcp_conn, udp_conn):
        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn
        self._dme_player_id = self._tcp._player_id

        self._loop.create_task(self._dmetcpagg())
        self._dmetcp_queue = queue.Queue()
        self._dmeudp_queue = queue.Queue()


    def process(self, serialized: dict):
        '''
        A packet has been added to the queue to update the model
        '''
        #logger.debug(f"Processing: {serialized}")

        if serialized['packet'] == 'medius.rt.serverconnectcomplete':
            return

        if serialized['packet'] == 'medius.rt.clientappsingle':
            for dme_packet in serialized['packets']:
                self.process_dme_packet(serialized['src_player'], dme_packet, serialized['protocol'])


    def process_dme_packet(self, src_player, dme_packet, protocol):
        if protocol == 'TCP':
            self.process_dme_packet_tcp(src_player, dme_packet)
        elif protocol == 'UDP':
            pass
        else:
            logger.error("Unknown protocl: " + protocol)
            raise Exception()

    def process_dme_packet_tcp(self, src_player, dme_packet):
        logger.debug(f"Processing DME TCP packet (src:{src_player}): {dme_packet}")

        responses = []
        if dme_packet['packet'] == 'medius.dme_packets.playerconnected2':
            resp_packet = playerconnected2.PlayerConnected2Serializer.build(self._dme_player_id, dme_packet['key'])
            dst_player = src_player
            responses = [[dst_player, resp_packet]]
        elif dme_packet['packet'] == 'medius.dme_packets.commonsixteen':
            resp_packet = commonsixteen.CommonSixteenSerializer.build(self._dme_player_id, src_player)
            dst_player = src_player
            responses = [[dst_player, resp_packet]]



        for resp in responses:
            logger.debug(f"Resp: {resp}")
            self._dmetcp_queue.put(resp)



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
                        pass

                    final_pkt = rtpacket_to_bytes(pkt)

                    self._tcp.queue(final_pkt)

            await asyncio.sleep(0.1)


    def _dmeudpagg(self, serialized_packet):
        pass
