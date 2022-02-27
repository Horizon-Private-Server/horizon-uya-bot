# 2022-02-27 09:53:59,770 blarg | INFO | 1 | udp_0209_movement_update; data:{'r1': '7F', 'cam1_y': 136, 'cam1_x': 218, 'vcam1_y': '00', 'r2': '7F', 'cam2_y': 136, 'cam2_x': 218, 'vcam2_y': '00', 'r3': '7F', 'cam3_y': 136, 'cam3_x': 218, 'v_drv': '00', 'r4': '7F', 'cam4_y': 136, 'cam4_x': 218, 'buffer': '00', 'coord': [21461, 24323, 2174], 'packet_num': 183, 'flush_type': 0, 'last': '6D006E006E007300', 'type': 'movement'}


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
ax.scatter(xs,ys,zs, s=2)
#surf = ax.plot_trisurf(xs, ys, zs, alpha=.1)

ax.set_zlim3d(100, 4100)
plt.show()
