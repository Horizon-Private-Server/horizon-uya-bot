from datetime import datetime
import random

class Arsenal:
    def __init__(self, weapons:list=['flux', 'blitz', 'rocket', 'grav', 'n60'], enabled:bool=True):
        self.enabled = enabled
        self.weapons = {
            'flux':
                {
                    'cooldown': 1.45,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'blitz':
                {
                    'cooldown': 1.45,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'rocket':
                {
                    'cooldown': 1.7,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'grav':
                {
                    'cooldown': 1.43,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'n60':
                {
                    'cooldown': .25,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
        }


    def fire_weapon(self, weapon: str):
        weapon_fired_bool = False
        hit_bool = False

        # Fire weapon
        if (random.random() < self.weapons[weapon]['shoot_rate']) and ((datetime.now().timestamp() - self.weapons[weapon]['last_ts_fired']) > self.weapons[weapon]['cooldown']):
            weapon_fired_bool = True
            self.weapons[weapon]['last_ts_fired'] = datetime.now().timestamp()

            # Fire weapon HIT
            if random.random() < self.weapons[weapon]['hit_rate']:
                hit_bool = True

        return weapon_fired_bool, hit_bool

    def __str__(self):
        return f"Arsenal; enabled:{self.enabled} weapons:{self.weapons}"
