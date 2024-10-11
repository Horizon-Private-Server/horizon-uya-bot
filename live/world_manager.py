from live.game_state import GameState

class WorldManager:
    def __init__(self, world_timeout=600):
        self._worlds = {}
        self._world_timeout = world_timeout


    def update(self, data_point: dict, serialized_data):
        world_id = data_point['dme_world_id']
        
        if world_id not in self._worlds.keys():
            self._worlds[world_id] = GameState(world_id, self._world_timeout)
        else:
            self._worlds[world_id].update()

        if serialized_data.name == 'tcp_0004_tnw' and serialized_data.tnw_type == 'tNW_GameSetting':
            print(serialized_data)
            self._worlds[world_id].tnw_gamesetting_update(data_point['src'], serialized_data.data)

        if serialized_data.name == 'udp_0209_movement_update':
            self._worlds[world_id].movement_update(data_point['src'], serialized_data.data)

        if serialized_data.name == 'tcp_0204_player_killed':
            self._worlds[world_id].health_update(data_point['src'], 0)
            self._worlds[world_id].player_killed(serialized_data.killer_id, serialized_data.killed_id, serialized_data.weapon)

        if serialized_data.name == 'tcp_0003_broadcast_lobby_state':
            msgs = [key for key in serialized_data.data.keys() if key[0:3] == 'msg']

            for msg in msgs:
                if serialized_data.data[msg]['type'] == 'health_update':
                    self._worlds[world_id].health_update(data_point['src'], serialized_data.data[msg]['health'])

                if serialized_data.data[msg]['type'] == 'weapon_upgraded':
                    self._worlds[world_id].set_weapon_upgrades(data_point['src'], serialized_data.data[msg])

        if serialized_data.name == 'tcp_020C_info' and serialized_data.subtype[2:] == '_flag_update' and serialized_data.data['flag_update_type'][2:] == '_capture':
            self._worlds[world_id].flag_capture(data_point['src'])


        if serialized_data.name == 'tcp_020A_player_respawned':
            self._worlds[world_id].health_update(data_point['src'], 100)
            self._worlds[world_id].reset_arsenal(data_point['src'])

    def check_timeouts(self):
        worlds_to_remove = []
        for world_id in self._worlds.keys():
            if self._worlds[world_id].timed_out():
                worlds_to_remove.append(world_id)

        for world_id in worlds_to_remove:
            del self._worlds[world_id]

    def to_json(self):
        worlds = []
        for world in self._worlds.values():
            worlds.append(world.to_json())
        return worlds