import trimesh
import numpy as np
import networkx as nx
print("Reading map")

map = 'aquatos_sewers'

mesh = trimesh.load(f'/home/fourbolt/Documents/uya/thug/maps/meshes/{map}.stl', process=False)

points = np.array(mesh.vertices).astype(int)
edge_idxes = mesh.edges

G = nx.Graph()

for edge_src, edge_dst in edge_idxes:
    G.add_edge(tuple(points[edge_src].astype(int)), tuple(points[edge_dst].astype(int)))

print("Done")

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# print(len(G.edges))
# i = 0
# for src, dst in G.edges:
#     print(i)
#     i+=1
#     xs = [src[0], dst[0]]
#     ys = [src[1], dst[1]]
#     zs = [src[2], dst[2]]
#     ax.plot3D(xs,ys,zs, c='tab:blue', linewidth=1)

xlim = ax.get_xlim()
zlim = ax.get_zlim()
xdiff = (xlim[1] - xlim[0]) / 2

zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

zlim = [zmid - xdiff, zmid + xdiff]

ax.set_zlim3d(zlim[0], zlim[1])
#ax.set_xlim3d(23000,23500)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
plt.tight_layout()
plt.show()
