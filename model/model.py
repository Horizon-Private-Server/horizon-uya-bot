
import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

class Model:
    def __init__(self, loop, tcp_conn, udp_conn):
        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn
        self._dme_player_id = self._tcp._player_id

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
