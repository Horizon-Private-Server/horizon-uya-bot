import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from scipy.optimize import least_squares
from scipy.linalg import orthogonal_procrustes
import os

class LocalTransform():
    def __init__(self, map_name, debug=False, write_transforms=False):
        self._map_name = map_name
        self._debug = debug

        self.script_dir = os.path.dirname(__file__)

        if debug:
            # Retrain on points
            R, t = self.read_and_train(map_name)
        else:
            R = np.load(os.path.join(self.script_dir, 'local_coordinates', f'{map_name}_R.npy'))
            t = np.load(os.path.join(self.script_dir, 'local_coordinates', f'{map_name}_t.npy'))

        self.R = R
        self.t = t

        if write_transforms:
            np.save(f'local_coordinates/{map_name}_R.npy', R)
            np.save(f'local_coordinates/{map_name}_t.npy', t)


    def global_to_local_transformation(global_coords, local_coords):
        """
        Approximates the transformation matrix to transform from global space to local space.

        Parameters:
        - global_coords: A Nx3 numpy array of global coordinates (N points).
        - local_coords: A Nx3 numpy array of corresponding local coordinates.

        Returns:
        - R: 3x3 numpy array representing the rotation matrix.
        - t: 1x3 numpy array representing the translation vector.
        """

        # Calculate centroids (mean) of global and local coordinates
        centroid_global = np.mean(global_coords, axis=0)
        centroid_local = np.mean(local_coords, axis=0)

        # Centering the coordinates around the centroids
        centered_global = global_coords - centroid_global
        centered_local = local_coords - centroid_local

        # Compute covariance matrix H
        H = np.dot(centered_global.T, centered_local)

        # Perform Singular Value Decomposition (SVD) on H
        U, S, Vt = np.linalg.svd(H)

        # Calculate optimal rotation matrix R
        R = np.dot(U, Vt)

        # Ensure R is a proper rotation matrix (det(R) = 1)
        if np.linalg.det(R) < 0:
            Vt[2, :] *= -1  # Flip the last row of Vt
            R = np.dot(U, Vt)

        # Calculate translation vector t
        t = centroid_local - np.dot(R, centroid_global)

        return R, t

    def transform_raw_global(self, map_name, point):
        new_point = point

        if map_name == 'marcadia_palace':
            new_point[0] = new_point[0] * .5
            new_point[1] = new_point[1] - 39000
            new_point[2] = new_point[2] + 10000

        return new_point

    def read_and_train(self, map_name):
        with open(f'local_coordinates/{map_name}.json', 'r') as f:
            inputs = json.loads(f.read())
            print(len(inputs))
            for i in range(len(inputs)):
                inputs[i][0] = self.transform_raw_global(map_name, inputs[i][0])

        global_coords = np.array([z[0] for z in inputs])
        local_coords = np.array([z[1] for z in inputs])

        R, t = self.estimate_transformation(global_coords, local_coords)

        print("Rotation Matrix R:")
        print(R)
        print("\nTranslation Vector t:")
        print(t)

        pred_dists = defaultdict(list)
        for transform_func in [self.estimate_transformation]:
            print(transform_func.__name__)

            R, t = transform_func(global_coords, local_coords)

            # Transform coordinate from global to local space
            for global_coord, local_coord in inputs:
                pred_local = self.global_to_local_single(global_coord, R, t)
                dist = self.euclidean_distance(local_coord, pred_local)
                pred_dists[transform_func.__name__].append(dist)
                print(global_coord, local_coord, pred_local, dist)

        for key, value in pred_dists.items():
            print(key, np.mean(value))

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection="3d")
        # ax.set_title("Raw points")
        # xs = [n[1][0] for n in inputs]
        # ys = [n[1][1] for n in inputs]
        # zs = [n[1][2] for n in inputs]
        # ax.scatter(xs, ys, zs, s=1, c='tab:blue')
        # xlim = ax.get_xlim()
        # zlim = ax.get_zlim()
        # xdiff = (xlim[1] - xlim[0]) / 2

        # zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

        # zlim = [zmid - xdiff, zmid + xdiff]

        # ax.set_zlim3d(zlim[0], zlim[1])
        # ax.set_xlabel("x")
        # ax.set_ylabel("y")
        # ax.set_zlabel("z")
        # plt.tight_layout()
        # plt.show()

        return R, t



    def transform_error(self, params, global_coords, local_coords):
        R = params[:9].reshape((3, 3))
        t = params[9:]
        
        transformed_global = np.dot(global_coords, R.T) + t
        error = np.linalg.norm(transformed_global - local_coords)
        
        return error

    def estimate_transformation(self, global_coords, local_coords):
        params0 = np.random.rand(12)  # Initial guess for parameters (R and t)
        #params0 = initial_estimate(global_coords, local_coords)
        result = least_squares(self.transform_error, params0, args=(global_coords, local_coords), method='dogbox', ftol=1e-8, xtol=1e-8, max_nfev=100000)
        
        R = result.x[:9].reshape((3, 3))
        t = result.x[9:]
        
        return R, t


    def global_to_local_single(self, coord_global, R, t):
        """
        Transforms a single coordinate from global space to local space using rotation matrix R and translation vector t.

        Parameters:
        - coord_global: A 1x3 numpy array representing the coordinate in global space.
        - R: 3x3 numpy array representing the rotation matrix.
        - t: 1x3 numpy array representing the translation vector.

        Returns:
        - coord_local: A 1x3 numpy array representing the coordinate in local space.
        """
        # Ensure coord_global is a 1x3 numpy array
        coord_global = np.array(coord_global).reshape(3,)

        # Apply rotation and translation
        coord_local = np.dot(R, coord_global) + t

        return coord_local


    def euclidean_distance(self, point1, point2):
        """
        Computes the Euclidean distance between two points in 3D space.

        Parameters:
        - point1: A tuple or list representing the coordinates of the first point (x1, y1, z1).
        - point2: A tuple or list representing the coordinates of the second point (x2, y2, z2).

        Returns:
        - distance: The Euclidean distance between the two points.
        """
        # Convert points to NumPy arrays for vectorized computation
        point1 = np.array(point1)
        point2 = np.array(point2)

        # Calculate the squared differences for each coordinate
        squared_diff = (point2 - point1) ** 2

        # Sum the squared differences and take the square root to get the distance
        distance = np.sqrt(np.sum(squared_diff))

        return distance



if __name__ == '__main__':
    LocalTransform('marcadia_palace', debug=False, write_transforms=False)