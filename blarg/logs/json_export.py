import json

coords = set()
import glob

files = glob.glob("*.log")
for fl in files:
    with open(fl, 'r') as f:
        for line in f:
            if 'coord' in line:
                coord = line.split("'coord': ")[-1].split(", '")[0]
                coords.add(eval(coord.replace("[",'(').replace("]",')')))

# READ IN
with open('points.json', 'r') as f:
    points = json.loads(f.read())
    for i in range(len(points)):
        points[i] = tuple(points[i])
    coords = coords.union(points)


# WRITE OUT
with open('points.json', 'w') as f:
    f.write(json.dumps(list(coords)))


########################### PART 2
import json

coords = set()
import glob

files = glob.glob("*.log")
for fl in files:
    with open(fl, 'r') as f:
        for line in f:
            if 'coord' in line:
                coord = line.split("'coord': ")[-1].split(", '")[0]
                coords.add(eval(coord.replace("[",'(').replace("]",')')))

# READ IN
with open('points.json', 'r') as f:
    points = json.loads(f.read())
    for i in range(len(points)):
        points[i] = tuple(points[i])
    coords = coords.union(points)

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

xs = [c[0] for c in coords]
ys = [c[1] for c in coords]
zs = np.array([c[2] for c in coords])


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(xs,ys,zs, s=1)
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
