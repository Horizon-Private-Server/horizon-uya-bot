import numpy as np
import json
import networkx as nx
import os
from scipy.spatial import distance
from datetime import datetime
import trimesh

import sys
sys.path.append("/home/fourbolt/Documents/uya/thug")
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

    def read_map(self, map_name):
        logger.info("Loading map mesh ...")
        mesh = trimesh.load(f'/home/fourbolt/Documents/uya/thug/maps/meshes/{self.map}.stl', process=False)

        self.points = np.array(mesh.vertices).astype(int)
        edge_idxes = mesh.edges

        G = nx.Graph()

        for edge_src, edge_dst in edge_idxes:
            G.add_edge(tuple(self.points[edge_src].astype(int)), tuple(self.points[edge_dst].astype(int)))

        return G
        #
        # # Prune the points
        # points_selected = []
        # points_to_pick_from = points_raw
        # while points_to_pick_from != []:
        #     point_to_add = points_to_pick_from.pop()
        #     points_selected.append(point_to_add)
        #
        #     points_to_check = np.array(points_to_pick_from)
        #     if points_to_check.shape[0] == 0:
        #         continue
        #
        #     distances = distance.cdist(points_to_check, [point_to_add], 'euclidean')
        #     for i in range(distances.shape[0]):
        #         if distances[i][0] < self.prune_dist:
        #             points_to_pick_from.remove(list(points_to_check[i]))
        #
        # self.points = np.array(points_selected)
        # logger.info("Done.")
        #
        # ## Generate the graph
        # logger.info("Generating graph ...")
        # G = nx.Graph()
        #
        # for i in range(len(self.points)):
        #     point = self.points[i]
        #     distances = distance.cdist(self.points, [point], 'euclidean')
        #     # Get all coordinates within moveable distances
        #     moveables = (distances > min_dist) & (distances < max_dist)
        #     points_connected = self.points[moveables.flatten(),:]
        #     distances = distances[moveables.flatten()]
        #
        #     # print(point)
        #     # print(points_connected)
        #     # print(distances)
        #     #G.add_node(tuple(point))
        #     for i in range(len(distances)):
        #         G.add_edge(tuple(point), tuple(points_connected[i]), weight=distances[i][0])
        #         # Calculate the distance between this connected point and
        #     #print("Nodes in G: ", G.nodes(data=True))
        # logger.info("Done.")
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
    print("Reading map")
    map = Map('aquatos_sewers')
    print("Done")
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    G = map.G

    # Create the 3D figure
    print("Graphing ...")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot the nodes - alpha is scaled by "depth" automatically
    nodes = np.array(G.nodes)
    xs = [n[0] for n in nodes]
    ys = [n[1] for n in nodes]
    zs = [n[2] for n in nodes]
    ax.scatter(xs, ys, zs, s=5, c='tab:blue')

    print(len(G.edges))
    i = 0
    for src, dst in G.edges:
        print(i)
        i+=1
        xs = [src[0], dst[0]]
        ys = [src[1], dst[1]]
        zs = [src[2], dst[2]]
        ax.plot3D(xs,ys,zs, c='tab:blue', linewidth=1)

    xlim = ax.get_xlim()
    zlim = ax.get_zlim()
    xdiff = (xlim[1] - xlim[0]) / 2

    zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

    zlim = [zmid - xdiff, zmid + xdiff]

    ax.set_zlim3d(zlim[0], zlim[1])
    ax.set_xlim3d(23000,23500)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.tight_layout()
    plt.show()
