from connections.mastcp import MasTcp
from connections.mlstcp import MlsTcp
from connections.dmetcp import DmeTcp
from connections.dmeudp import DmeUdp

from connections.states.fail import Fail
from connections.states.start import Start


class NetworkManager:
    def __init__(self, loop, config):
        self.alive = True
        self.loop = loop

        self._mas = MasTcp(self.loop, config.mas_ip, config.mas_port, config.username, config.password)


        self.loop.run_until_complete(self._mas.connect_tcp())

        self.loop.run_until_complete(self._mas.begin_session())

        self.loop.run_until_complete(self._mas.account_login())

        self.loop.run_until_complete(self._mas.close())

        # Initialize connections
        self._mls = MlsTcp(self.loop, self._config, self._mas_conn._session_key, self._mas_conn._access_key, self._config['mls_ip'], self._config['mls_port'])
        
        
        
        
        
        # self._tcp_conn = DmeTcp(self.loop, self._config)

        # self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_1())
        
        # logger.info("Initializing DME UDP ...")
        # self._udp_conn = DmeUdp(self.loop, self._config, self._config['dmeudp_ip'], self._config['dmeudp_port'])

        # # Connect to DME world
        # self.loop.run_until_complete(self._udp_conn.connect_to_dme_world(self._tcp_conn.get_player_id()))
        # self.loop.run_until_complete(self._tcp_conn.connect_to_dme_world_stage_2())



    async def update(self):
        
        pass


