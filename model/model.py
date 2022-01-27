
import logging
logger = logging.getLogger('thug.model')
logger.setLevel(logging.DEBUG)

class Model:
    def __init__(self):
        self._

    def process(self, serialized: dict):
        '''
        A packet has been added to the queue to update the model
        '''
        logger.debug(serialized)
        
