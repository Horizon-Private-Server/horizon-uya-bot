import numpy as np
import json
import networkx as nx
import os
from scipy.spatial import distance
from datetime import datetime
import random
import sys

from butils.utils import *
from maps.transforms import LocalTransform

import logging
logger = logging.getLogger("thug.map")
logger.setLevel(logging.DEBUG)

siege_ctf_respawn_coords = {
    "bakisi_isles": {"red": [12446, 17599, 12802], "blue": [36762, 15792, 12832]},
    "hoven_gorge": {"red": [9883, 9623, 4170], "blue": [19874, 22622, 4269]},
    "outpost_x12": {"red": [10290, 14710, 6144], "blue": [45047, 15683, 6151]},
    "korgon_outpost": {"red": [28328, 21108, 6145], "blue": [14090, 22676, 6145]},
    "metropolis": {"red": [47061, 14929, 21463], "blue": [49628, 28445, 21463]},
    "blackwater_city": {"red": [13004, 9759, 5156], "blue": [15165, 24379, 5156]},
    "command_center": {"red": [21523, 24181, 2174], "blue": [20766, 22551, 2174]},
    'aquatos_sewers': {"red": [12680, 17857, 6736], "blue": [17312, 12087, 6379]},
    "blackwater_docks": {"red": [25773, 18112, 60224], "blue": [25527, 23871, 60224]},
    "marcadia_palace": {"red": [33990, 54644, 7413], "blue": [27500, 54131, 7424]},
}

def search_heuristic(node1, node2):
    return distance.cdist([node1], [node2], 'euclidean')[0]

class Map:
    def __init__(self, map_name:str):
        self.map = map_name
        self.path_cache = None
        self.local_transform = None

        self.cboot_factor = 5
        self.cboot_distance = 3000

    def read_map(self):
        start_time = datetime.now()
        logger.info(f"Loading map graph {self.map} ...")
        self.G = nx.read_edgelist(f"maps/graphs/{self.map}.edgelist",nodetype=eval, delimiter='|')
        self.points = np.array(self.G.nodes)
        logger.info(f"Loaded map in {(datetime.now() - start_time).total_seconds()} seconds!")

        logger.info(f"Loading map local transformation ...")
        self.local_transform = LocalTransform(self.map)


    def path(self, src, dst):


        src = tuple(src)
        dst = tuple(dst)

        # use_cboot = calculate_distance(src, dst) > self.cboot_distance

        if self.path_cache != None and len(self.path_cache) != 0:
            if calculate_distance(src, self.path_cache[0]) < 100 and calculate_distance(dst, self.path_cache[-1]) < 100:
                return self.path_cache.pop(0)
                # else: # Use cboot
                #     if len(self.path_cache) > self.cboot_factor:
                #         self.path_cache = self.path_cache[self.cboot_factor:]
                #         return self.path_cache.pop(0)
                #     return self.path_cache.pop(0)

        if not self.G.has_node(src):
            return src

        # if dst is not in the graph, use the closest point
        if not self.G.has_node(dst):
            # get the closest point as dst
            dst = self.find_closest_node(dst)

        try:
            path = nx.astar_path(self.G, src, dst, heuristic=search_heuristic)
            if len(path) == 1:
                return path[0]
            elif len(path) > 1:
                # if use_cboot:
                #     if (len(path)-1) > self.cboot_factor:
                #         self.path_cache = path[self.cboot_factor:]
                #         return self.path_cache.pop(0)
                #     else:
                #         self.path_cache = path[1:]
                #         return path[1]
                # else:
                self.path_cache = path[1:]
                return path[1]
            else:
                raise Exception(f"Unknown path length: {path}")
        except nx.exception.NetworkXNoPath:
            logger.exception("No Path Found:")
            return src

    def find_closest_node(self, dst):
        distances = distance.cdist(self.points, [dst], 'euclidean')
        min_idx = np.where(distances == np.amin(distances))[0][0]
        return tuple(self.points[min_idx])

    # def find_closest_node_from_list(self, lst, dst, dist):
    #     distances = distance.cdist(lst, [dst], 'euclidean')
    #     idx, dist_closest = min(enumerate(distances), key=lambda x: abs(x[1]-dist))
    #     return lst[idx]

    def get_random_coord(self):
        return tuple(random.choice(np.array(self.points)))

    def get_random_coord_connected(self, coord):
        return list(random.choice(list(self.G.neighbors(tuple(coord)))))
    
    def get_random_coord_nearby(self, coord, dist=500):
        variance = 100
        dist_min = dist-variance
        dist_max = dist+variance
        distances = distance.cdist(self.points, [coord], 'euclidean').flatten()
        # logger.info(coord)
        # logger.info(sum(distances < dist_max))
        # logger.info(sum(distances < dist_min))
        # logger.info(sum((distances < dist_max) & (distances > dist_min)))
        points = self.points[np.where((distances < dist_max) & (distances > dist_min))]
        point_chosen = list(tuple(random.choice(points)))
        logger.info(f"Distance from coord: {calculate_distance(coord, point_chosen)}")
        return point_chosen

    def get_random_coord_connected_close(self, src_coord, dst_coord):
        if not self.G.has_node(src_coord):
            src_coord = self.find_closest_node(src_coord)

        if random.random() < .4:
            return self.get_random_coord_connected(src_coord)
        return self.path(src_coord, dst_coord)


        if not self.G.has_node(dst_coord):
            # get the closest point as dst
            dst_coord = self.find_closest_node(dst_coord)

        connected = list(self.G.neighbors(tuple(dst_coord)))

        logger.info(connected)
        distances = distance.cdist(connected, [dst_coord])
        distance_to_src = distance.cdist([src_coord],[dst_coord])[0][0]

        for i in range(len(distances)):
            if distances[i][0] < distance_to_src:
                logger.info(connected[i])
                return connected[i]
        return self.path(src_coord, dst_coord)


    def get_respawn_location(self, team_color, game_mode):
        if game_mode == 'Deathmatch':
            return self.get_random_coord()

        # Siege/CTF
        return self.find_closest_node(siege_ctf_respawn_coords[self.map][team_color])

    def __str__(self):
        return f"Map(name={self.map})"

    def transform_global_to_local(self, point):
        transformed = self.local_transform.transform_global_to_local(point)
        return [int(transformed[0]), int(transformed[1]), int(transformed[2])]
    
    def transform_local_to_global(self, point):
        transformed = self.local_transform.transform_local_to_global(point)
        return [int(transformed[0]), int(transformed[1]), int(transformed[2])]
    

if __name__ == '__main__':
    print("Reading map")
    map = Map('aquatos_sewers')
    print("Done")
