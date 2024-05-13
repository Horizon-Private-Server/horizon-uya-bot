import asyncio

from model.objects.crate import Crate
from medius.dme_packets import tcp_020C_info

import logging
logger = logging.getLogger('thug.healthcrate')
logger.setLevel(logging.INFO)

class HealthCrate(Crate):
    def __init__(self, model, description, id, location, master=0, owner=0):
        super().__init__(model, description, id, location, master, owner)