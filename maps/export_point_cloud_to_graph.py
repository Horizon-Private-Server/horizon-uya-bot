import numpy as np
import open3d as o3d
import json
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance
import os
import sys

figsize = (12, 12)
map_name = 'bakisi_isles'
display_raw_points = False
display_downsampled = False

# Adjust this in order to make the grid further apart or closer together
point_cloud_voxel_size = 50
# Adjust this to connect closer/farther points
distance_connected_variance = 30

print("-- Loading in point cloud ...")
with open(os.path.join(f'point_clouds',f'{map_name}.json'), 'r') as f:
#with open('../blarg/logs/points.json', 'r') as f:
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
G = nx.Graph()

for i in range(len(nodes)):
    this_nearest_distance = nearest_distances[i]
    this_node = nodes[i]
    distances = distance.cdist(nodes, [this_node], 'euclidean')
    # Get all coordinates within moveable distances
    moveables = (distances < this_nearest_distance+distance_connected_variance)
    points_connected = nodes[moveables.flatten(),:]
    distances = distances[moveables.flatten()]

    for i in range(len(distances)):
        if tuple(this_node) != tuple(points_connected[i]):
            G.add_edge(tuple(this_node), tuple(points_connected[i]), weight=distances[i][0])
        # Calculate the distance between this connected point and
    #print("Nodes in G: ", G.nodes(data=True))
print("Done.")
'''
print("-- Plotting Graph ...")
# The graph to visualize
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
plt.tight_layout()
plt.show()
'''
print("-- Writing Graph to graphs folder ...")
nx.write_edgelist(G, os.path.join('graphs', f"{map_name}.edgelist"), delimiter='|')
