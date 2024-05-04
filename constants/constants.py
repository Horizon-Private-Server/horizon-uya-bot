import json
import os

VALID_GAME_MODES = {
    'marcadia_palace': {'Deathmatch'}
}


SPECIAL_SYMBOLS = {
    'default': '08',
    'blue': '00',
    'green': '0A',
    'pink': '0B',
    'white': '0C',
    'gray': '0D',
    'black': '0E',
    'cross': '10',
    'circle': '11',
    'triangle': '12',
    'square': '13',
    'l1': '14',
    'r1': '15',
    'l2': '16',
    'r2': '17',
    'analog_left': '18',
    'analog_right': '19',
    'select': '1A',
}


# Movement generally is 0.068 seconds between each movement packet
MAIN_BOT_LOOP_TIMER = 0.068

script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'blitz_angles.json') ,'r') as f:
    BLITZ_ANGLES = json.loads(f.read())

with open(os.path.join(script_dir, 'grav_dist_to_time.json') ,'r') as f:
    GRAV_TIMING = json.loads(f.read())

CTF_FLAG_ID_MAP = {
    'command_center': {'131000F7': 'red_flag', '141000F7': 'blue_flag'},
    'aquatos_sewers': {'121000F7': 'red_flag', '131000F7': 'blue_flag'},
    'blackwater_docks': {'0E1000F7': 'red_flag', '0F1000F7': 'blue_flag'},
    'marcadia_palace': {'131000F7': 'red_flag', '141000F7': 'blue_flag'},
}

CTF_FLAG_LOCATIONS = {
    'command_center': {'red': [22401, 23381, 2296], 'blue': [19863, 23373, 2296]},
    'aquatos_sewers': {'red': [25666, 17724, 60224], 'blue': [25675, 24307, 60226]},
    'blackwater_docks': {'red': [12621, 17510, 6765], 'blue': [17104, 11738, 6409]},
    'marcadia_palace': {'red': [34431, 53967, 7362], 'blue': [26813, 54001, 7364]},
}

def parse_object_id(object_id, map='marcadia_palace'):
    if map in {'command_center', 'aquatos_sewers', 'blackwater_docks', 'marcadia_palace'}:
        if object_id not in CTF_FLAG_ID_MAP[map].keys():
            return None
        return CTF_FLAG_ID_MAP[map][object_id]

    return None


def get_flag_location(map='marcadia_palace', team='red'):
    if map in {'command_center', 'aquatos_sewers', 'blackwater_docks', 'marcadia_palace'}:
        return CTF_FLAG_LOCATIONS[map][team]
    return [0,0,0]

def get_blitz_angle(x_angle):
    return BLITZ_ANGLES[str(x_angle)]

def get_grav_timing(distance):
    '''
    Return the time in seconds for a gravity bomb to explode at a specific location given the distance between the caster
    and the destination location
    '''
    if str(int(distance)) not in GRAV_TIMING.keys():
        return -1
    return GRAV_TIMING[str(int(distance))]

DEATHMATCH_MAP = {
    0: 'blue',
    1: 'red',
    2: 'green',
    3: 'orange',
    4: 'yellow',
    5: 'purple',
    6: 'aqua',
    7: 'pink',
}



TEAM_MAP = {
    '00': 'blue',
    '01': 'red',
    '02': 'green',
    '03': 'orange',
    '04': 'yellow',
    '05': 'purple',
    '06': 'aqua',
    '07': 'pink',
    'FF': 'NA'
}

SKIN_MAP = {
    '00': 'ratchet',
    '01': 'robo',
    '02': 'thug',
    '03': 'tyhrranoid',
    '04': 'blarg',
    '05': 'ninja',
    '06': 'snow man',
    '07': 'bruiser',
    '08': 'gray',
    '09': 'hotbot',
    '0A': 'gladiola',
    '0B': 'evil clown',
    '0C': 'beach bunny',
    '0D': 'robo rooster',
    '0E': 'buginoid',
    '0F': 'branius',
    '10': 'skrunch',
    '11': 'bones',
    '12': 'nefarious',
    '13': 'trooper',
    '14': 'constructobot',
    '15': 'dan',
    'FF': 'NA'
}

KILL_MSG_MAP = {
    '00': 'butchered',
    '01': 'liquidated',
    '02': 'extirpated',
    '03': 'exterminated',
    '04': 'mousetrapped',
    '05': 'kervorked',
    '06': 'flatlined',
    '07': 'abolished',
    '08': 'eviscerated',
    '09': 'cremated',
    '0A': 'dismembered',
    '0B': 'euthanized',
    '0C': 'tomahawked',
    '0D': 'expunged',
    '0E': 'devastated',
    '0F': 'smoked',
}

WEAPON_MAP = {
    '01': 'n60',
    '02': 'blitz',
    '03': 'flux',
    '04': 'rocket',
    '05': 'grav',
    '06': 'mine',
    '07': 'lava',
    '09': 'morph',
    '0A': 'wrench',
    '0B': 'hyper',
    '0C': 'holo shield',
    'FF': 'NA'
}


# FLUSH: 16
ANIMATION_MAP = {
    'forward': '4B',
    'backward': '6A',
    'left': '7A',
    'right': '5B',
    'forward-left': '43D6',
    'forward-right': '42D2',
    'backward-left': '63DE',
    'backward-right': '535A',
    'jump': 'EF',
    'crouch': '9C', # side flip: use flush = 148, spam crouch: 32
    'shoot': 'BD',
    'forward-shoot': '45D2',
    'jump-shoot': 'B77B'
}
