from connections.mastcp import MasTcp
from connections.mlstcp import MlsTcp
from connections.dmetcp import DmeTcp
from connections.dmeudp import DmeUdp

from connections.states.fail import Fail
from connections.states.start import Start


class NetworkManager:
    def __init__(self):
        self.alive = True

        self._mas = MasTcp()
        self._mls = MlsTcp()
        self._dmetcp = DmeTcp()
        self._dmeudp = DmeUdp()

        self.state = Start(self)

    async def update(self):
        
        self.state.update()


    def transition_state(self, new_state: str):
        
        self.state.exit()
        self.

