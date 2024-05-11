import asyncio

from model.objects.uyaobject import UyaObject
from medius.dme_packets import tcp_020C_info

import logging
logger = logging.getLogger('thug.crate')
logger.setLevel(logging.INFO)

class Crate(UyaObject):
    def __init__(self, model, description, id, location, master=0, owner=0):
        super().__init__(model, id, location, master, owner)
        self.description = description
        self.respawn_time = 30 # seconds
        self.respawning = False

    async def respawn(self):
        if self.respawning:
            return

        self.respawning = True
        await asyncio.sleep(45)

        if self.model.game_state.player.player_id == self.owner:
            logger.info("SENDING RESPAWN!")
            self.model.dmetcp_queue.put(['B', tcp_020C_info.tcp_020C_info(subtype=f'p{self.model.game_state.player.player_id}_crate_respawn', timestamp=self.model.game_state.player.time, object_type=self.id, data={})])

        logger.info(f"NOT SENDING RESPAWN: {self.model.game_state.player.player_id} | {self.owner}")
        self.respawning = False

    def __str__(self):
        return f"Crate; id:{self.id} master:{self.master} owner:{self.owner} respawning:{self.respawning} desc:{self.description}"