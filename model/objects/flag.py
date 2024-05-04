



flag_map = {
    'marcadia_palace': {
        'red': '441000F7',
        'blue': '431000F7'
    },
    'command_center': {
        'red': '131000F7',
        'blue': '141000F7',
    },
    'aquatos_sewers': {
        'red': '121000F7',
        'blue': '131000F7',
    },
    'blackwater_docks': {
        'red': '441000F7',
        'blue': '431000F7',
    },
    'bakisi_isles': {
        'red': '441000F7',
        'blue': '431000F7',
    },
}


class Flag:
    def __init__(self, color, map):
        self._color = color
        self._map = map
        self._id = flag_map[map][color]

    
    def __str__(self):
        return f"Flag; color:{self._color} id:{self._id}"