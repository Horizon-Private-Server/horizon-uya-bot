from live.game_state import GameState

class WorldManager:
    def __init__(self, world_timeout=10):
        self._worlds = {}
        self._world_timeout = world_timeout


    def update(self, data_point: dict, serialized_data):
        world_id = data_point['dme_world_id']
        
        if world_id not in self._worlds.keys():
            self._worlds[world_id] = GameState(world_id, self._world_timeout)


        if serialized_data.name == 'tcp_0004_tnw' and serialized_data.tnw_type == 'tNW_PlayerData':
            print(serialized_data)
            #self.game_state.tnw_playerdata_update(src_player, dme_packet.data)

        if serialized_data.name == 'tcp_0004_tnw' and serialized_data.tnw_type == 'tNW_GameSetting':
            print(serialized_data)
            #self.game_state.tnw_gamesetting_update(src_player, dme_packet.data)


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