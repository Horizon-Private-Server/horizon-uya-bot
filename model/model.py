
import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

class Model:
    def __init__(self, loop, tcp_conn, udp_conn):
        self._loop = loop
        self._tcp = tcp_conn
        self._udp = udp_conn

    def process(self, serialized: dict):
        '''
        A packet has been added to the queue to update the model
        '''
        #logger.debug(f"Processing: {serialized}")

        if serialized['packet'] == 'medius.rt.serverconnectcomplete':
            return

        if serialized['packet'] == 'medius.rt.clientappsingle':
            for dme_packet in serialized['packets']:
                self.process_dme_packet(serialized['src_player'], dme_packet)


    def process_dme_packet(self, src_player, dme_packet):
        logger.debug(f"Processing DME packet (src:{src_player}): {dme_packet}")
