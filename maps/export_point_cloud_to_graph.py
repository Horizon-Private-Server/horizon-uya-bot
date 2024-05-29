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

maps = [
    'aquatos_sewers',
    # 'bakisi_isles',
    # 'blackwater_city',
    'blackwater_docks',
    'command_center',
    # 'hoven_gorge',
    # 'korgon_outpost',
    'marcadia_palace',
    # 'metropolis',
    # 'outpost_x12',
]

display_raw_points = False
display_downsampled = False
plot_connected_graph = False
write_graph = True


for map_name in maps:
    print(f"******* Processing map: {map_name}")
    figsize = (12, 12)


    # Adjust this in order to make the grid further apart or closer together
    point_cloud_voxel_size = 10
    # Adjust this to connect closer/farther points
    distance_connected_variance = [20,40]

    print("-- Loading in point cloud ...")
    with open(os.path.join(f'point_clouds',f'{map_name}.json'), 'r') as f:
        points = np.array(json.loads(f.read()))

    print(f"-- Points loaded: {points.shape}")

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



    ## Generate the graph
    print("-- Generating graph ...")
    start_time = datetime.now()
    G = nx.Graph()

    for i in range(len(nodes)):
        if (i+1) % 10000 == 0:
            print(f"Processed {i+1} nodes.")
        this_nearest_distance = nearest_distances[i]
        this_node = nodes[i]
        distances = distance.cdist(nodes, [this_node], 'euclidean')
        # Get all coordinates within moveable distances

        # print(this_node)
        # print(len(distances))
        # print(type(distances))
        # print(distances)    
        # print(distance_mask)
        # print(len(nodes))
        # sys.exit()

        #moveables = (distances < this_nearest_distance+distance_connected_variance)
        moveables = (distances < distance_connected_variance[1]) & (distances > distance_connected_variance[0])
        points_connected = nodes[moveables.flatten(),:]
        distances = distances[moveables.flatten()]

        for i in range(len(distances)):
            if tuple(this_node) != tuple(points_connected[i]):
                G.add_edge(tuple(this_node), tuple(points_connected[i]), weight=distances[i][0])


    print("Done.")
    end_time = datetime.now()
    print(f"Total nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} ")
    total_time = (end_time - start_time).total_seconds() / 60
    print(f"Took {total_time} minutes to generate graph!")

    ## Connect disconnected components
    print("-- Fixing disconnected components ...")
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
        print("Adding edges to components...")
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
            G.add_edge(*edge_to_add)
        
        # Recalculate the components
        components = list(nx.connected_components(G))

    print("Done.")
    end_time = datetime.now()
    print(f"Total nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} ")
    total_time = (end_time - start_time).total_seconds() / 60
    print(f"Took {total_time} minutes to fix components!")



    if plot_connected_graph:
        print("-- Plotting Graph ...")
        # The graph to visualize

        #nx.draw(G, with_labels=False, node_color='skyblue', font_color='black', font_weight='bold')
        #plt.show()

        xs = [n[0] for n in G]
        ys = [n[1] for n in G]
        zs = [n[2] for n in G]

        # Create the 3D figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

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

    if write_graph:
        print("-- Writing Graph to graphs folder ...")
        start_time = datetime.now()
        nx.write_edgelist(G, os.path.join('graphs', f"{map_name}.edgelist"), delimiter='|')
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"Took {total_time} seconds to write graph!")
        #nx.write_graphml(G, os.path.join('graphs', f"{map_name}.graphml"))