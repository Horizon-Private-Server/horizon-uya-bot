import numpy as np
import json
import networkx as nx
import os
from scipy.spatial import distance
from datetime import datetime

import sys
sys.path.append("/home/fourbolt/Documents/uya/thug")
from utils.utils import *

import logging
logger = logging.getLogger("thug.map")
logger.setLevel(logging.DEBUG)

class Map:
    def __init__(self, map_name, min_dist, max_dist):

        self.map = map_name
        self.min_dist = min_dist
        self.max_dist = max_dist

        start_time = datetime.now().timestamp()
        self.G = self.read_map(map_name, min_dist, max_dist)
        logger.info(f"Loaded map in {datetime.now().timestamp() - start_time} seconds!")

    def read_map(self, map_name, min_dist, max_dist):
        with open(os.path.join('maps', f'{map_name}.json'), 'r') as f:
            self.points = np.array(json.loads(f.read()))
            points = self.points

        G = nx.Graph()

        for i in range(points.shape[0]):
            point = points[i]
            distances = distance.cdist(points, [point], 'euclidean')
            # Get all coordinates within moveable distances
            moveables = (distances > min_dist) & (distances < max_dist)
            points_connected = points[moveables.flatten(),:]
            distances = distances[moveables.flatten()]

            # print(point)
            # print(points_connected)
            # print(distances)
            G.add_node(tuple(point))
            for i in range(len(distances)):
                G.add_edge(tuple(point), tuple(points_connected[i]), weight=distances[i])
                # Calculate the distance between this connected point and
            #print("Nodes in G: ", G.nodes(data=True))
        return G

    def path(self, src, dst, distance_to_move=20):

        src = tuple(src)
        dst = tuple(dst)

        if not self.G.has_node(src):
            return src

        # if dst is not in the graph, use the closest point
        if not self.G.has_node(dst):
            # get the closest point as dst
            dst = self.find_closest_node(dst)

        try:
            path = nx.dijkstra_path(self.G, src, dst)
            if len(path) == 1:
                return path[0]
            elif len(path) > 1:
                return self.find_closest_node_from_list(path[1:], src, distance_to_move)
            else:
                raise Exception(f"Unknown path length: {path}")
        except nx.exception.NetworkXNoPath:
            logger.warning("No Path Found!")
            return src

    def find_closest_node(self, dst):
        distances = distance.cdist(self.points, [dst], 'euclidean')
        min_idx = np.where(distances == np.amin(distances))[0][0]
        return tuple(self.points[min_idx])

    def find_closest_node_from_list(self, lst, dst, dist):
        distances = distance.cdist(lst, [dst], 'euclidean')
        idx, dist_closest = min(enumerate(distances), key=lambda x: abs(x[1]-dist))
        return lst[idx]


# map = Map('command_center', 10, 50)
# x = [22397, 23012, 2117]
# y = [22340, 23955, 2104]
# print(map.path(x, y))
