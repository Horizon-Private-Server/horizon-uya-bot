from datetime import datetime
import random

class Arsenal:
    def __init__(self, weapons:list=['flux', 'blitz', 'grav'], enabled:bool=True):
        self.enabled = enabled
        self.weapons = {
            'flux':
                {
                    'upgrade': 'v1',
                    'kills': 0,
                    'cooldown': 1.45,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'blitz':
                {
                    'upgrade': 'v1',
                    'kills': 0,
                    'cooldown': .6,
                    'shoot_rate': 1,
                    'hit_rate': 0,
                    'last_ts_fired': datetime.now().timestamp()
                },
            'grav':
                {
                    'upgrade': 'v1',
                    'kills': 0,
                    'cooldown': 1.43,
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

    def set_weapon_upgrades(self, upgrades:dict):
        for weapon_name in self.weapons.keys():
            self.weapons[weapon_name]['upgrade'] = upgrades[weapon_name]

    def reset_upgrades(self):
        for weapon_name in self.weapons.keys():
            self.weapons[weapon_name]['upgrade'] = 'v1'
            self.weapons[weapon_name]['kills'] = 0
    
    def update_from_profile(self, profile):
        if profile.overall_skill == 10:
            self.weapons['flux']['hit_rate'] = .5
            self.weapons['grav']['hit_rate'] = .7
        elif profile.overall_skill == 9:
            self.weapons['flux']['hit_rate'] = .3
            self.weapons['grav']['hit_rate'] = .5
        elif profile.overall_skill == 8:
            self.weapons['flux']['hit_rate'] = .25
            self.weapons['grav']['hit_rate'] = .45
        elif profile.overall_skill == 7:
            self.weapons['flux']['hit_rate'] = .15
            self.weapons['grav']['hit_rate'] = .25
        elif profile.overall_skill == 6:
            self.weapons['flux']['hit_rate'] = .1
            self.weapons['grav']['hit_rate'] = .2
        elif profile.overall_skill == 5:
            self.weapons['flux']['hit_rate'] = .05
            self.weapons['grav']['hit_rate'] = .1
        elif profile.overall_skill == 4:
            self.weapons['flux']['hit_rate'] = .05
            self.weapons['grav']['hit_rate'] = 0
        elif profile.overall_skill == 3:
            self.weapons['flux']['hit_rate'] = 0
            self.weapons['grav']['hit_rate'] = .1
        elif profile.overall_skill == 2:
            self.weapons['flux']['hit_rate'] = 0
            self.weapons['grav']['hit_rate'] = 0.05
        elif profile.overall_skill == 1:
            self.weapons['flux']['hit_rate'] = 0
            self.weapons['grav']['hit_rate'] = 0



    def dump_upgrades(self):
        result = {
            'lava': 'v1',
            'mine': 'v1',
            'grav': 'v1',
            'rocket': 'v1',
            'flux': 'v1',
            'blitz': 'v1',
            'n60': 'v1',
            'morph': 'v1',
        }
        for weapon in self.weapons.keys():
            result[weapon] = self.weapons[weapon]['upgrade']

        return result

    def killed_player(self, weapon:str) -> bool:
        '''
        Return true if we upgrade
        '''
        self.weapons[weapon]['kills'] += 1
        if self.weapons[weapon]['kills'] == 3:
            self.weapons[weapon]['upgrade'] = 'v2'
            return True
        return False

    def __str__(self):
        return f"Arsenal; enabled:{self.enabled} weapons:{self.weapons}"
