import json
import matplotlib.pyplot as plt
import numpy as np
import math

coords = []

side_movement_distance_avg = 31.196077764476275
forward_movement_distance_avg = 30.93488136292109
avg = 31.06547956369868

input_log = 'moving_forward.log'

with open(input_log, 'r') as f:
    for line in f:
        if 'coord' in line:
            coord = line.split("'coord': ")[-1].split(", '")[0]
            coords.append(eval(coord.replace("[",'(').replace("]",')')))

print(coords)



dists = []
for i in range(len(coords)-1):
    dist = math.dist(coords[i], coords[i+1])
    print(coords[i], coords[i+1], dist)
    dists.append(dist)

print("Average:", np.mean(dists))

def plot_coords(coords):
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

plot_coords(coords)