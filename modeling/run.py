import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import collada
from rtree import index  # Install using: pip install rtree

def print_geometry_info(geometry):
    print(f"\nGeometry ID: {geometry.id}, Name: {geometry.name}")
    for primitive in geometry.primitives:
        if isinstance(primitive, collada.triangleset.TriangleSet):
            print("  TriangleSet:")
        elif isinstance(primitive, collada.polylist.Polylist):
            print("  Polylist:")
        elif isinstance(primitive, collada.lineset.LineSet):
            print("  LineSet:")
        elif isinstance(primitive, collada.polygons.Polygons):
            print("  Polygons:")
        else:
            print("  Unknown Primitive Type:")
        
        print(f"    Material: {primitive.material}")
        print(f"    Vertex count: {len(primitive.vertex)}")
        if hasattr(primitive, 'index'):
            print(f"    Index count: {len(primitive.index)}")

geometry_name = 'collision_mesh'
# Load the .dae file
dae = collada.Collada('collision.dae')
print_geometry_info(dae.geometries[geometry_name])



def build_bvh(geometry):
    idx = index.Index()
    for i, primitive in enumerate(geometry.primitives):
        if isinstance(primitive, collada.polylist.Polylist):
            for poly in primitive.polygons:
                vertices = [primitive.vertex[j] for j in poly.vertices]
                min_x = min(v[0] for v in vertices)
                min_y = min(v[1] for v in vertices)
                min_z = min(v[2] for v in vertices)
                max_x = max(v[0] for v in vertices)
                max_y = max(v[1] for v in vertices)
                max_z = max(v[2] for v in vertices)
                bbox = (min_x, min_y, min_z, max_x, max_y, max_z)
                idx.insert(i, bbox)
    return idx

def ray_intersects_triangle_3d(p, d, v0, v1, v2):
    epsilon = 1e-8
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(d, edge2)
    a = np.dot(edge1, h)
    if -epsilon < a < epsilon:
        return False  # This means ray is parallel to the triangle
    f = 1.0 / a
    s = p - v0
    u = f * np.dot(s, h)
    if u < 0.0 or u > 1.0:
        return False
    q = np.cross(s, edge1)
    v = f * np.dot(d, q)
    if v < 0.0 or u + v > 1.0:
        return False
    t = f * np.dot(edge2, q)
    if t > epsilon:
        return True
    else:
        return False

def line_intersects_geometry_bvh_3d(geometry, A, B, bvh):
    A = np.array(A, dtype=np.float32)
    B = np.array(B, dtype=np.float32)
    direction = B - A

    for i in bvh.intersection((A[0], A[1], A[2], B[0], B[1], B[2])):
        primitive = geometry.primitives[i]
        if isinstance(primitive, collada.polylist.Polylist):
            for poly in primitive.polygons:
                vertices = [primitive.vertex[j] for j in poly.vertices]
                for i in range(len(vertices) - 2):
                    v0, v1, v2 = vertices[i], vertices[i + 1], vertices[i + 2]
                    if ray_intersects_triangle_3d(A, direction, v0, v1, v2):
                        return True
    return False

# Assuming there is only one geometry
geometry = dae.geometries[geometry_name]

# Build BVH
#bvh = build_bvh(geometry)

def check_triangles(geometry):
    for i, primitive in enumerate(geometry.primitives):
        if isinstance(primitive, collada.polylist.Polylist):
            for j, polygon in enumerate(primitive):
                if len(polygon.vertices) == 3:
                    print(f"Polygon {i}-{j} is a triangle.")
                else:
                    print(f"Polygon {i}-{j} is not a triangle (has {len(polygon.vertices)} vertices).")

check_triangles(geometry)