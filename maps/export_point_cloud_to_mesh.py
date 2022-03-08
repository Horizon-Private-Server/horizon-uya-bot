import numpy as np
import open3d as o3d
import json

map_name = 'aquatos_sewers'
n_triangles = 5000


with open(f'point_clouds/{map_name}.json', 'r') as f:
#with open('../blarg/logs/points.json', 'r') as f:
    points = np.array(json.loads(f.read()))

print(points)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)


distances = pcd.compute_nearest_neighbor_distance()
avg_dist = np.mean(distances)
radius = 2 * avg_dist

pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

#o3d.visualization.draw_geometries([pcd], point_show_normal=True)

bpa_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd,o3d.utility.DoubleVector([radius, radius * 2]))

# use # of triangles
dec_mesh = bpa_mesh.simplify_quadric_decimation(n_triangles)
dec_mesh.remove_degenerate_triangles()
dec_mesh.remove_duplicated_triangles()
dec_mesh.remove_duplicated_vertices()
dec_mesh.remove_non_manifold_edges()


o3d.io.write_triangle_mesh(f"meshes/{map_name}.stl", dec_mesh)

o3d.visualization.draw_geometries([dec_mesh])
