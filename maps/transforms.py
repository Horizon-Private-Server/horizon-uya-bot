import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from scipy.optimize import least_squares
from scipy.linalg import orthogonal_procrustes
import os

class LocalTransform():
    def __init__(self, map_name, debug=False, retrain=False, write_transforms=False):
        self._map_name = map_name
        self.script_dir = os.path.dirname(__file__)
        
        self._S = np.diag(np.array([0.00750688, 0.00450012, 0.03800826]))
        self._t = np.array([17145.18909699, 17245.74244416, 16840.92433734])

        if retrain:
            # Retrain on points
            S, t = self.read_and_train()
        else:
            S = np.load(os.path.join(self.script_dir, 'local_coordinates', f'{map_name}_S.npy'))
            t = np.load(os.path.join(self.script_dir, 'local_coordinates', f'{map_name}_t.npy'))

        if write_transforms:
            np.save(f'local_coordinates/{map_name}_S.npy', S)
            np.save(f'local_coordinates/{map_name}_t.npy', t)

        self.S = S
        self.t = t

        if debug:
            self.plot_predicted()


    def transform_global_to_local(self, point):
        return self.transform_point(point, self.S, self.t)
    
    def transform_local_to_global(self, point):
        return self.transform_point_reverse(point, self.S, self.t)

    def read_points(self):
        with open(f'local_coordinates/{self._map_name}.json', 'r') as f:
            inputs = json.loads(f.read())
            for i in range(len(inputs)):
                inputs[i][0] = inputs[i][0]

        global_coords = np.array([z[0] for z in inputs])
        local_coords = np.array([z[1] for z in inputs])

        return global_coords, local_coords

    def read_and_train(self):
        global_coords, local_coords = self.read_points()

        if type(self._S) is not None:
            print("RETRAIN!")
            global_coords = [self.transform_point(coord, self._S, self._t) for coord in global_coords]

        S, t = self.estimate_transformation(global_coords, local_coords)

        if type(self._S) is not None:
            S, t = self.combine_S_t([self._S, S], [self._t, t])

        return S, t

    def plot_predicted(self):
        global_coords, local_coords = self.read_points()

        pred_dists = []
        preds = []
        # Transform coordinate from global to local space
        for i in range(len(global_coords)):
            global_coord = global_coords[i]
            local_coord = local_coords[i]

            pred_local = self.transform_point(global_coord, self.S, self.t).astype(int)
            preds.append(pred_local)
            dist = self.euclidean_distance(local_coord, pred_local)
            pred_dists.append(dist)
            #print(global_coord, local_coord, pred_local, dist)

        print("Avg distance error: ", np.mean(pred_dists))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title("Raw points")
        xs = [n[0] for n in local_coords]
        ys = [n[1] for n in local_coords]
        zs = [n[2] for n in local_coords]
        ax.scatter(xs, ys, zs, s=1, c='tab:blue')
        xs = [n[0] for n in preds]
        ys = [n[1] for n in preds]
        zs = [n[2] for n in preds]
        ax.scatter(xs, ys, zs, s=1, c='tab:red')
        xlim = ax.get_xlim()
        zlim = ax.get_zlim()
        xdiff = (xlim[1] - xlim[0]) / 2

        zmid = zlim[0] + ((zlim[1] - zlim[0]) / 2)

        zlim = [zmid - xdiff, zmid + xdiff]

        ax.set_zlim3d(zlim[0], zlim[1])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        plt.tight_layout()
        plt.show()




    def transform_error(self, params, global_coords, local_coords):
        S = np.diag(params[:3])  # Scaling matrix
        t = params[3:]  # Translation vector

        transformed_global = np.dot(global_coords, S.T) + t
        error = np.linalg.norm(transformed_global - local_coords)
        
        return error


    def estimate_transformation(self, global_coords, local_coords):
        params0 = np.random.rand(6)  # Initial guess for parameters (S and t)
        result = least_squares(self.transform_error, params0, args=(global_coords, local_coords), method='dogbox', ftol=1e-8, xtol=1e-8, max_nfev=100000)

        print("Result X:", result.x)

        S = np.diag(result.x[:3])  # Extract scaling matrix
        t = result.x[3:]  # Extract translation vector

        print("Result S:", S)
        print("Result t:", t)
        
        # #scaling_factors = np.array([0.55395726, 0.31147699, 2.32106206])
        # scaling_factors = np.array([0.0075, 0.0045, .038])

        # # Create the scaling matrix
        # S = np.diag(scaling_factors)

        # print(S)

        # t = [17145, 17245, 16840]


        return S, t

    def transform_point(self, point, S, t):
        """
        Transform a single point from global coordinates to local coordinates.

        Args:
        point (numpy array): The point coordinates in global coordinates, shape (3,).
        S (numpy array): Scaling matrix, shape (3, 3).
        R (numpy array): Rotation matrix, shape (3, 3).
        t (numpy array): Translation vector, shape (3,).

        Returns:
        numpy array: The transformed point coordinates in local coordinates, shape (3,).
        """
        scaled_point = np.dot(S, point)

        # Apply translation
        translated_point = scaled_point + t

        return translated_point

    def transform_point_reverse(self, point, S, t):
        """
        Transform a single point from local coordinates to global coordinates.

        Args:
        point (numpy array): The point coordinates in local coordinates, shape (3,).
        S (numpy array): Scaling matrix, shape (3, 3).
        t (numpy array): Translation vector, shape (3,).

        Returns:
        numpy array: The transformed point coordinates in global coordinates, shape (3,).
        """
        # Reverse translation
        translated_point = point - t

        # Reverse scaling
        inverse_S = np.linalg.inv(S)
        unscaled_point = np.dot(inverse_S, translated_point).astype(int)
        return [unscaled_point[0], unscaled_point[1], unscaled_point[2]]


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


    def combine_S_t(self, scaling_matrices, translation_vectors):
        # Combine scaling matrices
        # combined_S = np.eye(3)  # Identity matrix as initial value
        # for S in scaling_matrices:
        #     combined_S = np.dot(combined_S, S)

        # # Combine translation vectors
        # combined_t = np.zeros(3)
        # for t in translation_vectors:
        #     combined_t += t

        # return combined_S, combined_t
        # Combine scaling matrices
        combined_S = np.dot(scaling_matrices[1], scaling_matrices[0])

        # Combine translation vectors
        combined_t = np.dot(scaling_matrices[1], translation_vectors[0]) + translation_vectors[1]

        return combined_S, combined_t

if __name__ == '__main__':
    LocalTransform('marcadia_palace', debug=True, retrain=False, write_transforms=False)