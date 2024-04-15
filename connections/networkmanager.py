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

        # MAS
        self._mas = MasTcp(self.loop, config.mas_ip, config.mas_port, config.username, config.password)
        self.loop.run_until_complete(self._mas.connect())
        self.loop.run_until_complete(self._mas.close())

        # MLS
        self._mls = MlsTcp(self.loop, config.mls_ip, config.mls_port, self._mas.session_key, self._mas.access_key)
        self.loop.run_until_complete(self._mls.connect(config.world_id))

        # DME TCP
        self._dmetcp = DmeTcp(self.loop, self._mls.dme_ip, self._mls.dme_port, self._mls.dme_session_key, self._mls.dme_access_key, config.world_id)
        self.loop.run_until_complete(self._dmetcp.connect())

        # DME UDP
        self._dmeudp = DmeUdp(self.loop, self._dmetcp.dmeudp_ip, self._dmetcp.dmeudp_port, config.world_id, self._dmetcp.player_id)
        self.loop.run_until_complete(self._dmeudp.connect())

        # DME TCP FINAL
        self.loop.run_until_complete(self._dmetcp.connect_final())

        self.loop.create_task(self._mls.echo())
        self.loop.create_task(self._dmetcp.echo())
        self.loop.create_task(self._dmeudp.echo())


    def is_alive(self):
        return self._mls.alive and self._dmetcp.alive and self._dmeudp.alive

    async def kill(self):
        await self._mls.close()
        await self._dmetcp.close()
        self._dmeudp.close()