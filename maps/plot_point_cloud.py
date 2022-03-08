import trimesh
import numpy as np
import networkx as nx
import json
print("Reading point cloud")

map = 'aquatos_sewers'

# READ IN
with open(f'/home/fourbolt/Documents/uya/thug/maps/point_clouds/{map}.json', 'r') as f:
    points = json.loads(f.read())
    for i in range(len(points)):
        points[i] = tuple(points[i])

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

xs = [n[0] for n in points]
ys = [n[1] for n in points]
zs = [n[2] for n in points]

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(xs,ys,zs, s=1)

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
