
from butils.utils import *

class UyaObject():
    def __init__(self, model, id=-1, location=[0,0,0], master=0, owner=0):
        self.model = model
        self.id = id
        self.location = location
        self.master = master
        self.owner = owner
        self.touching_distance = 500 # in prod use 130

    def overlap(self, coord):
        # Check if another coordinate is close to this object
        dist = calculate_distance(self.location, coord)

        if dist < self.touching_distance:
            return True

        return False