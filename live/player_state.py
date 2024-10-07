from datetime import datetime

VALID_HP ={
    100,93,86,80,73,66,60,53,46,40,33,26,20,13,6,0
}
from model.arsenal import Arsenal


def get_closest_hp(input_number):
    return min(VALID_HP, key=lambda x: abs(x - input_number))

class PlayerState:
    def __init__(self, player_id:int=-1, account_id:int=-1, team:str='blue', username:str='UNKNOWN', skin:str='UNKNOWN', clan_tag:str='', rank:int=0):
        self.player_id = player_id
        self.account_id = account_id
        self.team = team
        self.username = username
        self.skin = skin

        self.coord_timestamp = datetime.now()
        self.coord = [0,0,0]
        self.cam_x = 0
        self.movement_packet_num = 0
        self.time = 0

        self.weapon = None
        self.is_dead = False
        self.animation = None
        self.prev_animation = None
        self.health = 100

        self.flag = None

        self.total_kills = 0

        self.arsenal = Arsenal()

    def respawn(self):
        self.is_dead = False
        self.weapon = None
        self.health = 100
        self.arsenal.reset_upgrades()

    def to_json(self):
        return {
            'player_id': self.player_id,
            'account_id': self.account_id,
            'team': self.team,
            'username': self.username,
            #'skin': self.skin,
            'coord': self.coord,
            'cam_x': self.cam_x,
            'weapon': self.weapon,
            'upgrades': self.arsenal.to_minimal_json(),
            'flag': self.flag.to_json() if self.flag else None,
            'health': self.health,
            'total_kills': self.total_kills,
        }
