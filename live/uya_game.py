import struct


MAP_BITMAP = {
    "00001":"Bakisi Isles",
    "00010":"Hoven Gorge",
    "00011":"Outpost x12",
    "00100":"Korgon Outpost",
    "00101":"Metropolis",
    "00110":"Blackwater City",
    "00111":"Command Center",
    "01001":"Aquatos Sewers",
    "01000": "Blackwater Dox",
    "01010":"Marcadia Palace",
}

TIME_BITMAP = {
    "000": 0,
    "001": 5,
    "010": 10,
    "011": 15,
    "100": 20,
    "101": 25,
    "110": 30,
    "111": 35,
}

MODE_BITMAP = { #3,4
    "00":"Siege",
    "01":"CTF",
    "10":"Deathmatch"
}

SUBMODE_BITMAP = {
    # "1":"no_teams", #13
    # "1":"base_attrition" #20
    "isTeams":13, #1 = yes, means u can swap teams only 0 in DM
    "isAttrition":20, #1 = yes #consitutes also as chaos ctf
}

WEAPONS = {
    0:"Lava Gun",
    1:"Morph O' Ray",
    2:"Mine Glove",
    3:"Gravity Bomb",
    4:"Rocket",
    5:"Blitz Cannon",
    6:"N60",
    7:"Flux Rifle"
}


def try_parse_value(func, num):
    # Function that ensures that if num is a negative integer, 
    # the result falls within the corresponding positive range 
    # of an unsigned 32-bit integer.
    try:
        return func(num)
    except:
        return func(num+2**32)

def uya_game_name_parser(game_name: str) -> str:
    return game_name[:15]

def uya_map_parser(generic_field_3: int, metadata: dict) -> str:
    if 'CustomMap' in metadata.keys() and metadata['CustomMap']:
        return metadata['CustomMap']

    # Pass in Generic Field 3 (integer)
    def internal_parser(raw_input) -> str:
        """Accepts generic_field_3 INTEGER number (which is 4 a byte long hex string)"""
        raw_int:int = int(raw_input) if type(raw_input) is not int else raw_input
        raw_hex:str = struct.pack("<I", raw_int).hex()
        first_byte_hex:str = raw_hex[0:2]
        int_base_16:int = int(first_byte_hex,16)
        bitmask:str = format(int_base_16, "#010b")[2:]
        _game_map:str = bitmask[:5]
        _game_map:str = MAP_BITMAP[_game_map]
        return _game_map

    try:
        game_map = try_parse_value(internal_parser, generic_field_3)
    except:
        game_map = "Unknown map!" 

    return game_map



def uya_time_parser(generic_field_3: int) -> int:
    # Pass in Generic Field 3 (integer)
    def internal_parser(raw_input) -> str:
        """Accepts generic_field_3 INTEGER number (which is 4 a byte long hex string)"""
        raw_int:int = int(raw_input) if type(raw_input) is not int else raw_input
        raw_hex:str = struct.pack("<I", raw_int).hex()
        first_byte_hex:str = raw_hex[0:2]
        int_base_16:int = int(first_byte_hex,16)
        bitmask:str = format(int_base_16, "#010b")[2:]
        game_time:str = bitmask[5:]
        game_time:str = TIME_BITMAP[game_time]
        return game_time

    try:
        game_timelimit = try_parse_value(internal_parser, generic_field_3)
    except:
        game_timelimit = "Unknown Time!" 

    return game_timelimit



def uya_gamemode_parser(generic_field_3: int) -> tuple[str, str]:
    # # Pass in Generic Field 3 (integer)
    def internal_parser(raw_input:int):
        '''Accepts generic_field_3 INTEGER number (which is 4 a byte long hex string)
        returns game MODE andd game SUBMODE/ type'''
        int_casted:int = int(raw_input) if type(raw_input) != 'int' else raw_input
        num_hex:str = struct.pack('<I', int_casted).hex()
        hex_last:str =num_hex[2:] #cut off the front 2 bytes
        int_cleaned:int = int(hex_last,16)
        num_bitmask:str = format(int_cleaned, "#026b")[2:]
        _game_mode:str = MODE_BITMAP[num_bitmask[3:5]] if num_bitmask[3:5] in MODE_BITMAP else "Unknown Game Mode"
        is_teams:bool = True if num_bitmask[SUBMODE_BITMAP['isTeams']] == '1' else False
        is_attrition:bool = True if num_bitmask[SUBMODE_BITMAP['isAttrition']]== '1' else False

        if _game_mode == MODE_BITMAP['00']:
            _game_type = "Attrition" if is_attrition else "Normal"
        elif _game_mode == MODE_BITMAP['01']:
            _game_type = "Chaos" if is_attrition else "Normal"
        elif _game_mode == MODE_BITMAP['10']:
            _game_type = "Teams" if is_teams else "FFA"
        else:
            _game_type = "Game Type Not Found"
        return _game_mode, _game_type
    try:
        game_mode, game_type = try_parse_value(internal_parser, generic_field_3)
    except:
        game_mode, game_type = 'Unkown Game Mode', 'Unknown Game Type'

    return game_mode, game_type



def uya_weapon_parser(player_skill_level:int) -> dict[str, bool]:
    result = {
        "Lava Gun": False,
        "Morph O' Ray": False,
        "Mine Glove": False,
        "Gravity Bomb": False,
        "Rocket": False,
        "Blitz Cannon": False,
        "N60": False,
        "Flux Rifle": False
    }
    try:
        bitmask:str = format(player_skill_level, "#010b")[-8:]
        for i in range(len(bitmask)-1, -1, -1):
            if bitmask[i] == "0":
                result[WEAPONS[i]] = True
        return result
    except Exception as e:
        print(e)
        return result