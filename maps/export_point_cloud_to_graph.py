import numpy as np
import open3d as o3d
import json
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance
import os
import sys
from datetime import datetime
from scipy.spatial.distance import euclidean
from copy import deepcopy
from scipy.spatial import distance
import gzip


#maps = [
    #'aquatos_sewers',
    # 'bakisi_isles',
    # 'blackwater_city',
    #'blackwater_docks',
    #'command_center',
    # 'hoven_gorge',
    # 'korgon_outpost',
    #'marcadia_palace',
    # 'metropolis',
    # 'outpost_x12',
#]

map_config = {
    # 'marcadia_palace': {
    #     # Adjust this in order to make the grid further apart or closer together
    #     'voxel_size': 10,
    #     # Adjust this to connect closer/farther points
    #     'distance_connected_variance': [20,40],
    #     'waypoints': {
    #         "edges": '1 -> 2;2 -> 1;2 -> 8;2 -> 7;2 -> 3;3 -> 2;3 -> 6;3 -> 4;4 -> 3;4 -> 5;4 -> 6;5 -> 4;5 -> 13;5 -> 6;6 -> 3;6 -> 4;6 -> 5;6 -> 12;6 -> 13;7 -> 2;7 -> 8;7 -> 10;8 -> 2;8 -> 7;8 -> 10;9 -> 10;10 -> 9;10 -> 8;10 -> 7;10 -> 11;10 -> 21;10 -> 20;11 -> 10;11 -> 12;11 -> 14;12 -> 6;12 -> 13;12 -> 11;13 -> 5;13 -> 6;13 -> 12;13 -> 15;13 -> 16;13 -> 14;14 -> 11;14 -> 13;14 -> 16;15 -> 13;15 -> 16;15 -> 17;16 -> 14;16 -> 13;16 -> 15;16 -> 17;16 -> 22;17 -> 15;17 -> 16;17 -> 22;18 -> 19;18 -> 20;18 -> 21;18 -> 22;19 -> 18;20 -> 10;20 -> 18;20 -> 21;21 -> 18;21 -> 10;21 -> 20;22 -> 16 ;22 -> 17;22 -> 18',
    #         "nodes": "1 -> [9838, 8847, 4183];2 -> [11342, 7753, 4260];3 -> [12978, 8277, 4244];4 -> [11413, 9635, 4333];5 -> [12932, 10122, 4169];6 -> [11643, 10822, 4166];7 -> [9478, 10953, 4165];8 -> [10592, 11661, 4165];9 -> [11479, 13793, 4167];10 -> [9508, 15681, 4184];11 -> [9757, 18205, 4261];12 -> [11970, 17921, 4171];13 -> [11294, 16058, 4236];14 -> [12598, 14012, 4136];15 -> [13243, 15910, 4104];16 -> [14515, 14291, 4124];17 -> [14889, 15905, 4096];18 -> [14247, 17547, 4049];19 -> [16323, 17630, 4004];20 -> [16316, 15996, 4006];21 -> [16298, 14239, 4013];22 -> [17770, 14447, 4057];23 -> [17851, 16705, 4093];24 -> [18730, 15818, 4099];25 -> [18753, 17096, 4103];26 -> [21010, 13929, 4187];27 -> [22908, 13404, 4307];28 -> [23083, 15993, 4209];29 -> [21232, 15558, 4179];30 -> [21502, 18224, 4164];31 -> [23136, 18546, 4207];32 -> [21644, 20721, 4166];33 -> [22818, 21699, 4263];34 -> [21350, 22580, 4439];35 -> [22898, 23685, 4388];36 -> [21375, 24624, 4395];37 -> [20074, 24491, 4383];38 -> [19966, 22060, 4277]"
    #     }
    # },
    'hoven_gorge': {
        # Adjust this in order to make the grid further apart or closer together
        'voxel_size': 100,
        # Adjust this to connect closer/farther points
        'distance_connected_variance': [20,40],
        'waypoints': {
            "edges": '1 -> 2;1 -> 7;2 -> 1;2 -> 3;3 -> 2;3 -> 5;4 -> 7;4 -> 8;4 -> 6;4 -> 5;5 -> 3;5 -> 4;5 -> 6;6 -> 5;6 -> 4;6 -> 8;6 -> 7;7 -> 1;7 -> 4;7 -> 6;7 -> 8;8 -> 7;8 -> 4;8 -> 6;8 -> 9;9 -> 8;9 -> 10;9 -> 13;9 -> 14;10 -> 9;10 -> 11;10 -> 13;11 -> 12;11 -> 13;11 -> 10;12 -> 11;12 -> 13;12 -> 18;12 -> 15;13 -> 9;13 -> 10;13 -> 11;13 -> 14;13 -> 12;13 -> 15;14 -> 9;14 -> 15;14 -> 16;14 -> 13;15 -> 12;15 -> 13;15 -> 14;15 -> 16;15 -> 17;15 -> 18;16 -> 14;16 -> 21;16 -> 15;16 -> 17;17 -> 15;17 -> 16;17 -> 18;17 -> 20;17 -> 21;17 -> 19;18 -> 12;18 -> 15;18 -> 17;18 -> 19;18 -> 20;19 -> 18;19 -> 17;19 -> 20;19 -> 23;20 -> 17;20 -> 18;20 -> 19;20 -> 21;20 -> 23;20 -> 24;20 -> 22;21 -> 16;21 -> 17;21 -> 20;21 -> 22;22 -> 21;22 -> 20;22 -> 23;22 -> 24;22 -> 26;23 -> 19;23 -> 20;23 -> 22;23 -> 24;23 -> 25;24 -> 20;24 -> 23;24 -> 25;24 -> 29;24 -> 22;24 -> 26;24 -> 30;25 -> 23;25 -> 24;25 -> 30;25 -> 29;26 -> 22;26 -> 24;26 -> 29;26 -> 27;27 -> 26;27 -> 29;27 -> 28;28 -> 27;28 -> 29;28 -> 30;28 -> 31;29 -> 26;29 -> 27;29 -> 28;29 -> 30;29 -> 25;29 -> 24;30 -> 25;30 -> 24;30 -> 29;30 -> 28;30 -> 31;30 -> 32;31 -> 30;31 -> 29;31 -> 28;32 -> 30;32 -> 33;32 -> 34;32 -> 38;33 -> 32;33 -> 34;33 -> 35;34 -> 33;34 -> 32;34 -> 38;35 -> 33;35 -> 36;36 -> 35;36 -> 37;37 -> 36;37 -> 38;38 -> 32;38 -> 34;38 -> 33;38 -> 37',
            "nodes": "1 -> [9838, 8847, 4183];2 -> [11342, 7753, 4260];3 -> [12978, 8277, 4244];4 -> [11413, 9635, 4333];5 -> [12932, 10122, 4169];6 -> [11643, 10822, 4166];7 -> [9478, 10953, 4165];8 -> [10592, 11661, 4165];9 -> [11479, 13793, 4167];10 -> [9508, 15681, 4184];11 -> [9757, 18205, 4261];12 -> [11970, 17921, 4171];13 -> [11294, 16058, 4236];14 -> [12598, 14012, 4136];15 -> [13243, 15910, 4104];16 -> [14515, 14291, 4124];17 -> [14889, 15905, 4096];18 -> [14247, 17547, 4049];19 -> [16323, 17630, 4004];20 -> [16316, 15996, 4006];21 -> [16298, 14239, 4013];22 -> [17770, 14447, 4057];23 -> [17851, 16705, 4093];24 -> [18730, 15818, 4099];25 -> [18753, 17096, 4103];26 -> [21010, 13929, 4187];27 -> [22908, 13404, 4307];28 -> [23083, 15993, 4209];29 -> [21232, 15558, 4179];30 -> [21502, 18224, 4164];31 -> [23136, 18546, 4207];32 -> [21644, 20721, 4166];33 -> [22818, 21699, 4263];34 -> [21350, 22580, 4439];35 -> [22898, 23685, 4388];36 -> [21375, 24624, 4395];37 -> [20074, 24491, 4383];38 -> [19966, 22060, 4277]"
        }
    },
}

##########################################################################################################################################

class MapGenerator:
    def __init__(self, map_name, config: dict):
        self._map = map_name
        print(f"******* Processing map: {map_name}")

        raw_points = self.read_raw_points()
        #self.plot_points(raw_points, title="Raw Points")

        downsampled = self.downsample(raw_points, voxel_size=config['voxel_size'])
        self.plot_points(downsampled, title="Downsampled Points")

        G = self.generate_graph(downsampled, variance=config['distance_connected_variance'])
        #self.plot_connected_graph(G, title="Main Graph")
        self.write_graph_to_file(G)

        print("******* Waypoint processing")
        
        waypoint_nodes = {}
        for node in config['waypoints']['nodes'].split(";"):
            node_num = node.split(" -> ")[0].strip()
            node_coord = eval(node.split(" -> ")[1].strip())
            node_coord = self.find_closest_node(G, node_coord)
            waypoint_nodes[node_num] = node_coord
        G_waypoints_only = nx.Graph()
        for edge in config['waypoints']['edges'].split(";"):
            node1 = waypoint_nodes[edge.split(" -> ")[0].strip()]
            node2 = waypoint_nodes[edge.split(" -> ")[1].strip()]
            weight = self.search_heuristic(node1, node2)
            G_waypoints_only.add_edge(tuple(node1), tuple(node2), weight=weight)

        G_waypoints = self.generate_waypoint_graph(G, G_waypoints_only)
        self.write_graph_to_file(G_waypoints_only, filename_suffix="waypoints_only")
        self.write_graph_to_file(G_waypoints, filename_suffix="waypoints")

        self.plot_waypoints(G_waypoints_only, G_waypoints)

        waypoint_cache = self.generate_waypoint_cache(G_waypoints_only, G_waypoints)
        self.write_waypoint_cache_to_file(waypoint_cache)

    def read_raw_points(self):
        print("-- Loading in point cloud ...")
        with open(os.path.join(f'point_clouds',f'{self._map}.json'), 'r') as f:
            points = np.array(json.loads(f.read()))
        print(f"Points loaded: {points.shape}")
        return points

    def downsample(self, points, voxel_size=10):
        print("-- Downsampling ...")
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        print("Downsampling voxel size ...")
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
        #o3d.visualization.draw_geometries([pcd])

        nearest_distances = np.array(pcd.compute_nearest_neighbor_distance())
        nodes = np.asarray(pcd.points).astype(int)
        print(f"Downsampled nodes shape: {nodes.shape}")
        print(f"Nearest Distances shape: {nearest_distances.shape}")
        return nodes

    def generate_graph(self, nodes, variance=[20,40]):
        ## Generate the graph
        print(f"-- Generating graph with {len(nodes)} nodes ...")

        print(type(nodes), nodes.shape)

        start_time = datetime.now()
        G = nx.Graph()

        for i in range(len(nodes)):
            if (i+1) % 10000 == 0:
                print(f"Processed {i+1} nodes.")
            #this_nearest_distance = nearest_distances[i]
            this_node = nodes[i]
            distances = distance.cdist(nodes, [this_node], 'euclidean')

            moveables = (distances < variance[1]) & (distances > variance[0])
            points_connected = nodes[moveables.flatten(),:]
            distances = distances[moveables.flatten()]

            for i in range(len(distances)):
                if tuple(this_node) != tuple(points_connected[i]):
                    G.add_edge(tuple(this_node), tuple(points_connected[i]), weight=distances[i][0])

        print("Done.")
        end_time = datetime.now()
        print(f"Total nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} ")
        total_time = (end_time - start_time).total_seconds() / 60
        print(f"Took {total_time:.2f} minutes to generate graph!")

        ## Connect disconnected components
        print(f"Fixing disconnected components ...")
        start_time = datetime.now()
        # Find all connected components
        components = list(nx.connected_components(G))
        print(f"Number of components: {len(components)}")
        for i, component in enumerate(components):
            print(f"Component {i+1}: {len(component)}")
        component_gt_limit = 20
        num_components_gt = 0
        for component in components:
            if len(component) > component_gt_limit:
                num_components_gt += 1
        
        if num_components_gt > 1:
            raise Exception(f"Found too many components with > {component_gt_limit} nodes!")

        # While there is more than one component
        while len(components) > 1:
            print(f"Adding edges to components (total components: {len(components)})...")
            # Initialize the minimum distance and the edge to add
            min_distance = float('inf')
            edge_to_add = None
            
            # Iterate over all pairs of components
            for i in range(len(components)):
                for j in range(i + 1, len(components)):
                    comp1 = components[i]
                    comp2 = components[j]
                    
                    # Iterate over all pairs of nodes (one from each component)
                    for node1 in comp1:
                        for node2 in comp2:
                            calc_dist = euclidean(node1, node2)
                            
                            # Update the minimum distance and edge to add
                            if calc_dist < min_distance:
                                min_distance = calc_dist
                                edge_to_add = (node1, node2)
            
            # Add the edge with the minimum distance
            if edge_to_add:
                G.add_edge(*edge_to_add, weight=self.search_heuristic(edge_to_add[0], edge_to_add[1]))
            
            # Recalculate the components
            components = list(nx.connected_components(G))

        print("Done.")
        end_time = datetime.now()
        print(f"Total nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} ")
        total_time = (end_time - start_time).total_seconds() / 60
        print(f"Took {total_time:.2f} minutes to fix components!")

        return G

    def generate_waypoint_graph(self, G, G_waypoints_only):
        G_result = nx.Graph()

        print("-- Generating G waypoints ...")
        for edge in G_waypoints_only.edges():
            # Generate 
            node1, node2 = edge

            path = nx.astar_path(G, node1, node2, heuristic=self.search_heuristic)

            for i in range(len(path)-1):
                node1 = [int(path[i][0]), int(path[i][1]), int(path[i][2])]
                node2 = [int(path[i+1][0]), int(path[i+1][1]), int(path[i+1][2])]
                G_result.add_edge(tuple(node1), tuple(node2), weight=self.search_heuristic(node1, node2))

        return G_result

    def generate_waypoint_cache(self, G_waypoints_only, G_waypoint):
        print("Generating waypoint cache ...")
        already_processed = set()
        waypoint_cache = {}
        start_time = datetime.now()
        for i, node1 in enumerate(G_waypoints_only):
            for node2 in G_waypoints_only:
                if node1 != node2 and (node1,node2) not in already_processed and (node2,node1) not in already_processed:
                    path = nx.astar_path(G_waypoint, node1, node2, heuristic=self.search_heuristic)
                    path = [[int(x[0]), int(x[1]), int(x[2])] for x in path]
                    waypoint_cache[f"{node1}|{node2}"] = path
                    already_processed.add((node1,node2))
                    already_processed.add((node2,node1))
            print(f"{i+1} / {len(G_waypoints_only)} ...",flush=True)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"Took {total_time:.2f} seconds to generate cache graph!")
        return waypoint_cache


    def write_graph_to_file(self, G, filename_suffix=None):
        print(f"-- Writing Graph to graphs folder ...")
        start_time = datetime.now()
        if filename_suffix == None:
            filename_suffix = ''
        else:
            filename_suffix = '_'+filename_suffix
        nx.write_edgelist(G, os.path.join('graphs', f"{self._map}{filename_suffix}.edgelist"), delimiter='|')
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"Took {total_time:.2f} seconds to write graph!")

    def write_waypoint_cache_to_file(self, waypoint_cache):
        with gzip.open(os.path.join('graphs', f"{self._map}_waypoint_cache.json.gz"), 'wt', encoding='utf-8', compresslevel=9) as f:
            json.dump(waypoint_cache, f)

    def plot_points(self, points, title="Points"):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title(title)
        xs = [n[0] for n in points]
        ys = [n[1] for n in points]
        zs = [n[2] for n in points]
        ax.scatter(xs, ys, zs, s=1, c='tab:blue')
        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2

        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

        zlim = [zmid - xdiff, zmid + xdiff]

        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        plt.tight_layout()
        plt.show()

    def plot_connected_graph(self, G, title="Connected Graph"):
        print(f"-- Plotting Graph ...")
        figsize = (12, 12)

        xs = [n[0] for n in G]
        ys = [n[1] for n in G]
        zs = [n[2] for n in G]

        # Create the 3D figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title(title)

        # Plot the nodes - alpha is scaled by "depth" automatically
        nodes = np.array(G.nodes)
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        #ax.scatter(xs, ys, zs, s=5, c='tab:blue')

        for src, dst in G.edges:
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
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(80, -60)
        print("Plotted!")
        plt.tight_layout()
        plt.show()

    def plot_waypoints(self, G_waypoints_only, G_waypoints):
        # Create the 3D figure
        figsize = (12, 12)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        nodes = np.array(G_waypoints.nodes)
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        ax.scatter(xs, ys, zs, s=5, c='tab:blue')

        nodes = np.array(G_waypoints_only.nodes)
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        ax.scatter(xs, ys, zs, s=20, c='tab:red')

        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2
        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)
        zlim = [zmid - xdiff, zmid + xdiff]
        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(80, -60)
        print("Plotted!")
        plt.tight_layout()
        plt.show()


    def search_heuristic(self, node1, node2):
        return distance.cdist([node1], [node2], 'euclidean')[0][0]

    def find_closest_node(self, G, src):
        distances = distance.cdist(np.array(G.nodes), [src], 'euclidean')
        min_idx = np.where(distances == np.amin(distances))[0][0]
        return tuple(np.array(G.nodes)[min_idx])

for map_name, config in map_config.items():
    MapGenerator(map_name, config)

    continue
    figsize = (12, 12)


    print("-- Loading in point cloud ...")
    with open(os.path.join(f'point_clouds',f'{self._map}.json'), 'r') as f:
        points = np.array(json.loads(f.read()))
    print(f"Points loaded: {points.shape}")


    print("-- Generating open3d point cloud ...")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    print("-- Downsampling voxel size ...")
    pcd = pcd.voxel_down_sample(voxel_size=point_cloud_voxel_size)
    #o3d.visualization.draw_geometries([pcd])

    nearest_distances = np.array(pcd.compute_nearest_neighbor_distance())
    nodes = np.asarray(pcd.points).astype(int)
    print(f"Downsampled nodes shape: {nodes.shape}")
    print(f"Nearest Distances shape: {nearest_distances.shape}")

    # ----------------------------- Raw points
    if display_raw_points == True:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title("Raw points")
        xs = [n[0] for n in points]
        ys = [n[1] for n in points]
        zs = [n[2] for n in points]
        ax.scatter(xs, ys, zs, s=1, c='tab:blue')
        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2

        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

        zlim = [zmid - xdiff, zmid + xdiff]

        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        plt.tight_layout()
        plt.show()

    # ----------------------------- Downsampled Points
    if display_downsampled == True:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title("Downsampled points")
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        ax.scatter(xs, ys, zs, s=1, c='tab:blue')
        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2
        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)
        zlim = [zmid - xdiff, zmid + xdiff]
        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        plt.tight_layout()
        plt.show()

    if plot_connected_graph or write_graph:
        generate_graph(map_name, nodes, graphtype='full', plot_connected=plot_connected_graph, write_graph_to_file=write_graph)

    if generate_waypoints:
        print("-- Waypoint processing ...")
        G = nx.read_edgelist(f"graphs/{map_name}.edgelist",nodetype=eval, delimiter='|')

        print("Downsampling voxel size for waypoints ...")
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(G.nodes)

        pcd = pcd.voxel_down_sample(voxel_size=waypoint_voxel_size)

        nearest_distances = np.array(pcd.compute_nearest_neighbor_distance())
        nodes = np.asarray(pcd.points).astype(int)

        nodes = np.array([find_closest_node(G, node) for node in nodes])

        generate_graph(map_name, nodes, graphtype='waypoint', plot_connected=False, write_graph_to_file=True)

        waypoint_large_G = nx.read_edgelist(f"graphs/{map_name}_waypoint.edgelist",nodetype=eval, delimiter='|')
        waypoint_G = nx.Graph()

        print("Generating Waypoint G ...")
        for edge in waypoint_large_G.edges():
            # Generate 
            node1, node2 = edge

            path = nx.astar_path(G, node1, node2, heuristic=search_heuristic)

            for i in range(len(path)-1):
                waypoint_G.add_edge(tuple(path[i]), tuple(path[i+1]), weight=search_heuristic(path[i], path[i+1]))

        nx.write_edgelist(waypoint_G, os.path.join('graphs', f"{map_name}_waypoint_deep.edgelist"), delimiter='|')

        # Generate cache for all waypoint combinations
        print("Generating waypoint cache ...")
        already_processed = set()
        waypoint_cache = {}
        start_time = datetime.now()
        for i, node1 in enumerate(waypoint_large_G):
            for node2 in waypoint_large_G:
                if node1 != node2 and (node1,node2) not in already_processed and (node2,node1) not in already_processed:
                    path = nx.astar_path(waypoint_G, node1, node2, heuristic=search_heuristic)
                    waypoint_cache[f"{node1}|{node2}"] = path       
                    already_processed.add((node1,node2))
                    already_processed.add((node2,node1))
            print(f"{i+1} / {len(waypoint_large_G)} ...",flush=True)
            #break

        with open(os.path.join('graphs', f"{map_name}_waypoint_cache.json"), 'w') as f:
            s = json.dumps(waypoint_cache)
            f.write(s)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"Took {total_time} seconds to generate cache graph!")

        # Create the 3D figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        # Plot the nodes - alpha is scaled by "depth" automatically
        nodes = np.array(waypoint_G.nodes)
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        ax.scatter(xs, ys, zs, s=5, c='tab:blue')

        nodes = np.array(waypoint_large_G.nodes)
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        zs = [n[2] for n in nodes]
        ax.scatter(xs, ys, zs, s=20, c='tab:red')

        # Plot edges as lines
        # for src, dst in waypoint_G.edges:
        #     xs = [src[0], dst[0]]
        #     ys = [src[1], dst[1]]
        #     zs = [src[2], dst[2]]
        #     ax.plot3D(xs,ys,zs, c='tab:green', alpha=.5, linewidth=1)

        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2
        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)
        zlim = [zmid - xdiff, zmid + xdiff]
        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(80, -60)
        print("Plotted!")
        plt.tight_layout()
        plt.show()

