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
#surf = ax.plot_trisurf(xs, ys, zs, alpha=.1)

ax.set_zlim3d(58000, 62000)
plt.show()
