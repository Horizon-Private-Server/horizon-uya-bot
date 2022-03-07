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
    def __init__(self, map_name:str, prune_dist:int, min_dist:int, max_dist:int):

        self.map = map_name
        self.prune_dist = prune_dist
        self.min_dist = min_dist
        self.max_dist = max_dist

        start_time = datetime.now().timestamp()
        self.G = self.read_map(map_name, min_dist, max_dist)
        logger.info(f"Loaded map in {datetime.now().timestamp() - start_time} seconds!")

    def read_map(self, map_name, min_dist, max_dist):
        with open(os.path.join('maps', f'{map_name}.json'), 'r') as f:
            points_raw = json.loads(f.read())
            self.points = np.array(points_raw)

        logger.info("Pruning points ...")
        # Prune the points
        points_selected = []
        points_to_pick_from = points_raw
        while points_to_pick_from != []:
            point_to_add = points_to_pick_from.pop()
            points_selected.append(point_to_add)

            points_to_check = np.array(points_to_pick_from)
            if points_to_check.shape[0] == 0:
                continue

            distances = distance.cdist(points_to_check, [point_to_add], 'euclidean')
            for i in range(distances.shape[0]):
                if distances[i][0] < self.prune_dist:
                    points_to_pick_from.remove(list(points_to_check[i]))

        self.points = np.array(points_selected)
        logger.info("Done.")

        ## Generate the graph
        logger.info("Generating graph ...")
        G = nx.Graph()

        for i in range(len(self.points)):
            point = self.points[i]
            distances = distance.cdist(self.points, [point], 'euclidean')
            # Get all coordinates within moveable distances
            moveables = (distances > min_dist) & (distances < max_dist)
            points_connected = self.points[moveables.flatten(),:]
            distances = distances[moveables.flatten()]

            # print(point)
            # print(points_connected)
            # print(distances)
            #G.add_node(tuple(point))
            for i in range(len(distances)):
                G.add_edge(tuple(point), tuple(points_connected[i]), weight=distances[i][0])
                # Calculate the distance between this connected point and
            #print("Nodes in G: ", G.nodes(data=True))
        logger.info("Done.")
        return G



    def path(self, src, dst, distance_to_move=20):
        def search_heuristic(node1, node2):
            return distance.cdist([node1], [node2], 'euclidean')[0]


        src = tuple(src)
        dst = tuple(dst)

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

if __name__ == '__main__':
    map = Map('command_center', 30, 20, 60)
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # The graph to visualize
    G = map.points

    xs = [n[0] for n in G]
    ys = [n[1] for n in G]
    zs = [n[2] for n in G]

    # fig = plt.figure()
    # ax = fig.add_subplot(projection='3d')
    # ax.scatter(xs,ys,zs, s=2)
    # #surf = ax.plot_trisurf(xs, ys, zs, alpha=.1)
    #
    # ax.set_zlim3d(100, 4100)
    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_zlabel('z')
    # plt.show()

    G = map.G

    # Create the 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot the nodes - alpha is scaled by "depth" automatically
    nodes = np.array(G.nodes)
    xs = [n[0] for n in nodes]
    ys = [n[1] for n in nodes]
    zs = [n[2] for n in nodes]
    ax.scatter(xs, ys, zs, s=5, c='tab:blue')

    for src, dst in G.edges:
        xs = [src[0], dst[0]]
        ys = [src[1], dst[1]]
        zs = [src[2], dst[2]]
        ax.plot3D(xs,ys,zs, c='tab:blue', linewidth=1)

    ax.set_zlim3d(100, 4100)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    plt.show()
