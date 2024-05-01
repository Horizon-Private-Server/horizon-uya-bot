
OBJECT_TYPES = {
    'marcadia_palace': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
        '101000F7': 'red_health',
        '0F1000F7': 'blue_health',
        '0E1000F7': 'turret_health',
    },
    'command_center': {
        '131000F7': 'red_flag',
        '141000F7': 'blue_flag',
    },
    'aquatos_sewers': {
        '121000F7': 'red_flag',
        '131000F7': 'blue_flag',
    },
    'blackwater_docks': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
    },
    'bakisi_isles': {
        '441000F7': 'red_flag',
        '431000F7': 'blue_flag',
    },
}


class ObjectManager():
    def __init__(self, map:str, game_mode:str):
        self._model = None
        self._map = map

        # ['Siege', 'CTF', 'Deathmatch']
        self._game_mode = game_mode

    def set_model(self, model):
        self._model = model