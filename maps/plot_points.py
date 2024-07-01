import matplotlib.pyplot as plt
import numpy as np
import json

with open('local_coordinates/marcadia_palace.json', 'r') as f:
    points = json.loads(f.read())

points = [point[1] for point in points]

print(points)

# Separate the list of points into x, y, and z coordinates
x, y, z = zip(*points)

# Create a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z)

# Add labels and title
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')
ax.set_title('3D Scatter Plot of Points')

plt.show()