

class PlayerState:
    def __init__(self, player_id:int, config:dict):
        self._config = config

        self.player_id = player_id

        self.account_id = self._config['account_id']
        self.team = self._config['team']
        self.username = self._config['username']
        self.skin = self._config['skin']
        self.clan_tag = self._config['clan_tag']

        rank_map = {
            1: '00C0A84400C0A84400C0A84400C0A8440000AF430000AF430000AF430000AF43',
            2: '00C0A84400C0A84400C0A84400C0A84400808443008084430080844300808443',
            3: '00C0A84400C0A84400C0A84400C0A84400000000000000000000000000000000',
            4: 'C8C8D444C8C8D444C8C8D444C8C8D44400808943008089430080894300808943'
        }
        self.rank = rank_map[self._config['bolt']]

        self.movement_packet_num = 0

        self.time = 0

    def gen_packet_num(self):
        self.movement_packet_num += 1
        if self.movement_packet_num == 256:
            self.movement_packet_num = 0
            return 0
        return self.movement_packet_num - 1

    def change_teams(self):
        team_change_map = {
            'blue': 'red',
            'red': 'green',
            'green': 'orange',
            'orange': 'yellow',
            'yellow': 'purple',
            'purple': 'aqua',
            'aqua': 'pink',
            'pink': 'blue'
        }
        self.team = team_change_map[self.team]
        return self.team
