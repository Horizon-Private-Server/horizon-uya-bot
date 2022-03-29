import numpy as np
import json
import networkx as nx
import os
from scipy.spatial import distance
from datetime import datetime
import random
import sys

from utils.utils import *

import logging
logger = logging.getLogger("thug.map")
logger.setLevel(logging.DEBUG)

class Map:
    def __init__(self, map_name:str):

        self.map = map_name

        start_time = datetime.now().timestamp()
        self.G = self.read_map(map_name)
        logger.info(f"Loaded map in {datetime.now().timestamp() - start_time} seconds!")

        self.path_cache = None

    def read_map(self, map_name):
        logger.info("Loading map graph ...")
        G = nx.read_edgelist(f"maps/graphs/{self.map}.edgelist",nodetype=eval, delimiter='|')
        self.points = np.array(G.nodes)
        return G

    def path(self, src, dst):
        def search_heuristic(node1, node2):
            return distance.cdist([node1], [node2], 'euclidean')[0]

        src = tuple(src)
        dst = tuple(dst)

        use_cboot = calculate_distance(src, dst) > 3000
        cboot_factor = 5

        if self.path_cache != None:
            if calculate_distance(src, self.path_cache[0]) < 100 and calculate_distance(dst, self.path_cache[-1]) < 100:
                if not use_cboot:
                    return self.path_cache.pop(0)
                else: # Use cboot
                    if len(self.path_cache) > cboot_factor:
                        self.path_cache = self.path_cache[cboot_factor:]
                        return self.path_cache.pop(0)
                    return self.path_cache.pop(0)

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
                if use_cboot:
                    if (len(path)-1) > cboot_factor:
                        self.path_cache = path[cboot_factor:]
                        return self.path_cache.pop(0)
                    else:
                        self.path_cache = path[1:]
                        return path[1]
                else:
                    self.path_cache = path[1:]
                    return path[1]
            else:
                raise Exception(f"Unknown path length: {path}")
        except nx.exception.NetworkXNoPath:
            logger.warning("No Path Found!")
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

if __name__ == '__main__':
    print("Reading map")
    map = Map('aquatos_sewers')
    print("Done")
