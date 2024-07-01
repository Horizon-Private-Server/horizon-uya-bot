import matplotlib.pyplot as plt
import json
import math
import argparse
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
import os

from sklearn.linear_model import RANSACRegressor


def calculate_distance(source_coord, dest_coord):
    return math.dist(source_coord, dest_coord)

class Transformer():
    def __init__(self, json_data={}):
        if json_data != {}:
            self.from_json(json_data)

    def train(self, global_coords: np.array, local_coords: np.array, debug=False):
        num_matrices_to_train = 1

        self.global_mins = {}
        self.global_maxes = {}
        self.local_mins = {}
        self.local_maxes = {}

        self.training_set = local_coords

        for i in range(3):
            self.global_mins[i] = int(np.min(global_coords[:,i]))
            self.global_maxes[i] = int(np.max(global_coords[:,i]))
            self.local_mins[i] = int(np.min(local_coords[:,i]))
            self.local_maxes[i] = int(np.max(local_coords[:,i]))

        #print(self.global_mins[0], self.global_maxes[0])

        transformed_coords = []
        for i in range(len(global_coords)):
            transformed_coords.append(self.range_transform(global_coords[i,:]))

        self.Ss, self.ts = self.estimate_transformation(transformed_coords, local_coords, num_matrices_to_train)

        output_coords = []
        for point in transformed_coords:
            output_coords.append(self.matrix_transform(self.Ss, self.ts, point))

        self.calculate_translation_error(output_coords, local_coords)

        for i in range(len(global_coords)):
            global_coord = global_coords[i]
            local_coord = local_coords[i]

            # Check global -> local
            new_local = self.transform_global_to_local(global_coord)
            dist = calculate_distance(new_local, local_coord)
            # if dist > 0:
            #     print("MAX DIST REACHED: ", global_coord, local_coord, new_local)

            new_global = self.transform_local_to_global(local_coord)
            dist = calculate_distance(new_global, global_coord)
            # if dist > 0:
            #     print(dist, "MAX DIST REACHED: ", global_coord, local_coord, new_global)


        if debug:
            x1 = [point[0] for point in output_coords]
            y1 = [point[1] for point in output_coords]
            z1 = [point[2] for point in output_coords]

            x2 = [point[0] for point in local_coords]
            y2 = [point[1] for point in local_coords]
            z2 = [point[2] for point in local_coords]

            # Creating a figure with 2 subplots
            fig = plt.figure(figsize=(18, 6))

            # First subplot
            ax1 = fig.add_subplot(131, projection='3d')
            ax1.scatter(x1, y1, z1, c='r', marker='o')
            ax1.set_title('Global Coordinates')
            ax1.set_xlabel('X axis')
            ax1.set_ylabel('Y axis')
            ax1.set_zlabel('Z axis')

            # Second subplot
            ax2 = fig.add_subplot(132, projection='3d')
            ax2.scatter(x2, y2, z2, c='b', marker='^')
            ax2.set_title('Local Coordinates')
            ax2.set_xlabel('X axis')
            ax2.set_ylabel('Y axis')
            ax2.set_zlabel('Z axis')

            # Second subplot
            ax3 = fig.add_subplot(133, projection='3d')
            ax3.scatter(x1, y1, z1, c='r', alpha=0.5, marker='o')
            ax3.scatter(x2, y2, z2, c='b', alpha=0.5, marker='^')
            #ax3.scatter(x2, y2, z2, c='g', alpha=0.5, marker='v')
            ax3.set_title('Both Coordinates')
            ax3.set_xlabel('X axis')
            ax3.set_ylabel('Y axis')
            ax3.set_zlabel('Z axis')

            plt.show()
    
    def global_overlap(self, point:list):
        # Check if the x coordinate is between our x min and xmax
        if self.global_mins[0] <= point[0] < self.global_maxes[0]:
            return 0
        
        return min(abs(self.global_mins[0] - point[0]), abs(self.global_maxes[0] - point[0]))

    def local_overlap(self, point:list):
        # Check if the x coordinate is between our x min and xmax
        if self.local_mins[0] <= point[0] < self.local_maxes[0]:
            return 0
        
        return min(abs(self.local_mins[0] - point[0]), abs(self.local_maxes[0] - point[0]))

    def transform_global_to_local(self, point:list):
        # Perform a full transformation, both range and matrix
        new_point = self.range_transform(point)
        new_point = self.matrix_transform(self.Ss, self.ts, new_point)
        return new_point

    def transform_local_to_global(self, point:list):
        # Perform a full transformation, both range and matrix
        new_point = self.matrix_transform_inverse(self.Ss, self.ts, point)
        new_point = self.range_transform_inverse(new_point)
        return new_point

    def range_transform(self, point: list):
        new_point = []
        for i in range(3):
            global_range = self.global_maxes[i] - self.global_mins[i]
            local_range = self.local_maxes[i] - self.local_mins[i]
            transformed = ((point[i] - self.global_mins[i]) / global_range) * local_range + self.local_mins[i]
            new_point.append(transformed)
        return new_point
    
    def range_transform_inverse(self, point: list):
        new_point = []
        for i in range(3):
            global_range = self.global_maxes[i] - self.global_mins[i]
            local_range = self.local_maxes[i] - self.local_mins[i]
            transformed = (((point[i] - self.local_mins[i]) / local_range) * global_range) + self.global_mins[i]
            new_point.append(transformed)
        return new_point

    def _single_matrix_transform(self, S, t, point):
        scaled_point = np.dot(S, point)
        # Apply translation
        translated_point = scaled_point + t
        return translated_point

    def _single_matrix_transform_inverse(self, S, t, point):
        translated_point = point - t
        # Reverse scaling
        inverse_S = np.linalg.inv(S)
        unscaled_point = np.dot(inverse_S, translated_point)
        return [unscaled_point[0], unscaled_point[1], unscaled_point[2]]

    def matrix_transform(self, Ss, ts, point):
        new_point = point

        for i in range(len(Ss)):
            S = Ss[i]
            t = ts[i]
            new_point = self._single_matrix_transform(S, t, new_point)
        return new_point
    
    def matrix_transform_inverse(self, Ss, ts, point):
        new_point = point

        for i in range(len(Ss)):
            S = Ss[i]
            t = ts[i]
            new_point = self._single_matrix_transform_inverse(S, t, new_point)
        return new_point

    def transform_error(self, params, global_coords, local_coords):
        S = np.diag(params[:3])  # Scaling matrix
        t = params[3:]  # Translation vector

        transformed_global = np.dot(global_coords, S.T) + t
        error = np.linalg.norm(transformed_global - local_coords)
        
        return error

    def estimate_transformation(self, global_coords, local_coords, num_matrices_to_train):
        Ss = []
        ts = []

        transformed_global = global_coords

        for _ in range(num_matrices_to_train):
            ransac = RANSACRegressor()
            ransac.fit(transformed_global, local_coords)

            # S and t can be derived from the fitted model
            S = ransac.estimator_.coef_
            t = ransac.estimator_.intercept_

            Ss.append(S)
            ts.append(t)

            transformed_global = [self._single_matrix_transform(S, t, point) for point in transformed_global]

        return Ss, ts

    def calculate_translation_error(self, global_points, local_points):
        dists = []
        for i in range(len(global_points)):
            transformed_point = global_points[i]
            local_point = local_points[i]
            dist = calculate_distance(transformed_point,local_point)
            dists.append(dist)

        mean_dist = np.mean(dists)
        median_dist = np.median(dists)
        sd_dist = np.std(dists)
        max_dist = max(dists)
        #print(f"DISTANCE ERROR: Mean:{mean_dist} Median:{median_dist} SD:{sd_dist} Max:{max_dist}")

    def __str__(self):
        return f"Transformer: local_mins:{self.local_mins}, local_max:{self.local_maxes} global_mins:{self.global_mins} global_maxes:{self.global_maxes}"

    def to_json(self) -> dict:
        return {
            "global_mins": self.global_mins,
            "global_maxes": self.global_maxes,
            "local_mins": self.local_mins,
            "local_maxes": self.local_maxes,
            "Ss": [S.tolist() for S in self.Ss],   
            "ts": [t.tolist() for t in self.ts],   
        }
    
    def from_json(self, json_data):
        self.global_mins = json_data["global_mins"]
        self.global_maxes = json_data["global_maxes"]
        self.local_mins = json_data["local_mins"]
        self.local_maxes = json_data["local_maxes"]
        self.Ss = [np.array(S) for S in json_data['Ss']]
        self.ts = [np.array(t) for t in json_data['ts']]

        for key in list(self.global_mins.keys()):
            self.global_mins[int(key)] = self.global_mins[key]
            del self.global_mins[key]
        for key in list(self.global_maxes.keys()):
            self.global_maxes[int(key)] = self.global_maxes[key]
            del self.global_maxes[key]
        for key in list(self.local_mins.keys()):
            self.local_mins[int(key)] = self.local_mins[key]
            del self.local_mins[key]
        for key in list(self.local_maxes.keys()):
            self.local_maxes[int(key)] = self.local_maxes[key]
            del self.local_maxes[key]




class LocalTransform():
    def __init__(self, map_name):
        self._map_name = map_name
        self.script_dir = os.path.dirname(__file__)

    def transform_global_to_local(self, point):
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

        # Get the transform that we need
        transform = None
        dist = 999999
        # Get the closest transform
        for t in self.transformers:
            new_dist = t.global_overlap(point)
            if new_dist == 0:
                transform = t
                break
            if new_dist < dist:
                dist = new_dist
                transform = t

        if transform == None:
            # Get closest
            
            print(f"No transform found for point: {point}")
        assert transform != None

        return transform.transform_global_to_local(point)


    def transform_local_to_global(self, point):
        # Get the transform that we need
        transform = None
        dist = 999999
        # Get the closest transform
        for t in self.transformers:
            new_dist = t.local_overlap(point)
            if new_dist == 0:
                transform = t
                break
            if new_dist < dist:
                dist = new_dist
                transform = t

        if transform == None:
            print(f"No transform found for point: {point}")
        assert transform != None

        res = transform.transform_local_to_global(point)

        return res
    
    def read_raw_points(self):
        global_coords = []
        local_coords = []
        with open(os.path.join(self.script_dir, 'local_coordinates_raw', f'{self._map_name}_raw.log')) as f:
            for line in f.readlines():
                if 'Movement:' in line and 'Flag:' in line and 'offset:' in line:
                    global_coord = eval(line.split("Movement:")[-1].split(" Flag:")[0].strip())
                    local_coord = eval(line.split("Flag:")[-1].split(", offset")[0].strip())
                    offset = eval(line.split("offset:")[-1].strip())

                    # Convert offset to from 0-255 -> 0 -> .9999
                    offset_new = [0,0,0]
                    offset_new[0] = offset[0] / 256
                    offset_new[1] = offset[1] / 256
                    offset_new[2] = offset[2] / 256

                    local_coord_new = [0,0,0]
                    local_coord_new[0] = local_coord[0] + offset_new[0]
                    local_coord_new[1] = local_coord[1] + offset_new[1]
                    local_coord_new[2] = local_coord[2] + offset_new[2]
                    
                    print(f"Converting: {local_coord}|{offset} -> {local_coord_new}")

                    #print(local_coord, local_coord_new)
                    if global_coord in global_coords:
                        print(f"Already have: {global_coord} skipping!")
                    else:
                        global_coords.append(global_coord)
                        local_coords.append(local_coord_new)

        global_coords = np.array(global_coords)
        local_coords = np.array(local_coords)
        return global_coords, local_coords

    def train(self, debug=False):
        print("Peprocessing points")
        global_coords, local_coords  = self.read_raw_points()
        print("Done preprocessing.")

        local_xmin = int(np.min(local_coords[:,0]))
        local_xmax = int(np.max(local_coords[:,0]))

        ranges = list(range(local_xmin, local_xmax, 5))
        if ranges[-1] < local_xmax:
            ranges[-1] = local_xmax

        self.transformers = []

        for i in range(len(ranges)-1):
            xmin = ranges[i]
            xmax = ranges[i+1]
            print(f"Processing range: {xmin} -> {xmax}")

            local_mask = (local_coords[:,0] >= xmin) & (local_coords[:,0] < xmax)
            range_global = global_coords[local_mask]
            range_local = local_coords[local_mask]

            transformer = Transformer()
            transformer.train(range_global, range_local, debug=debug)
            self.transformers.append(transformer)

        test_points = [self.transform_global_to_local(point) for point in global_coords]
        # Now check all raw points with their corresponding transformer
        dists = []
        for i in range(len(test_points)):
            transformed_point = test_points[i]
            local_point = local_coords[i]
            dist = calculate_distance(transformed_point,local_point)
            dists.append(dist)

        mean_dist = np.mean(dists)
        median_dist = np.median(dists)
        sd_dist = np.std(dists)
        max_dist = max(dists)
        print(f"DISTANCE ERROR: Mean:{mean_dist} Median:{median_dist} SD:{sd_dist} Max:{max_dist}")

        x1 = [point[0] for point in test_points]
        y1 = [point[1] for point in test_points]
        z1 = [point[2] for point in test_points]

        x2 = [point[0] for point in local_coords]
        y2 = [point[1] for point in local_coords]
        z2 = [point[2] for point in local_coords]

        # Creating a figure with 2 subplots
        fig = plt.figure(figsize=(8, 6))

        # Second subplot
        ax3 = fig.add_subplot(111, projection='3d')
        ax3.scatter(x1, y1, z1, c='r', alpha=0.5, marker='o')
        ax3.scatter(x2, y2, z2, c='b', alpha=0.5, marker='^')
        #ax3.scatter(x2, y2, z2, c='g', alpha=0.5, marker='v')
        ax3.set_title('Global To Local')
        ax3.set_xlabel('X axis')
        ax3.set_ylabel('Y axis')
        ax3.set_zlabel('Z axis')

        plt.show()

        test_points = [self.transform_local_to_global(point) for point in local_coords]
        # Now check all raw points with their corresponding transformer
        dists = []
        for i in range(len(test_points)):
            transformed_point = test_points[i]
            g = global_coords[i]
            dist = calculate_distance(transformed_point,g)
            dists.append(dist)
            #print(dist)

        mean_dist = np.mean(dists)
        median_dist = np.median(dists)
        sd_dist = np.std(dists)
        max_dist = max(dists)
        print(f"DISTANCE ERROR: Mean:{mean_dist} Median:{median_dist} SD:{sd_dist} Max:{max_dist}")


        x1 = [point[0] for point in test_points]
        y1 = [point[1] for point in test_points]
        z1 = [point[2] for point in test_points]

        x2 = [point[0] for point in global_coords]
        y2 = [point[1] for point in global_coords]
        z2 = [point[2] for point in global_coords]

        # Creating a figure with 2 subplots
        fig = plt.figure(figsize=(8, 6))

        # Second subplot
        ax3 = fig.add_subplot(111, projection='3d')
        ax3.scatter(x1, y1, z1, c='r', alpha=0.5, marker='o')
        ax3.scatter(x2, y2, z2, c='b', alpha=0.5, marker='^')
        #ax3.scatter(x2, y2, z2, c='g', alpha=0.5, marker='v')
        ax3.set_title('Local To Global')
        ax3.set_xlabel('X axis')
        ax3.set_ylabel('Y axis')
        ax3.set_zlabel('Z axis')

        plt.show()

    def save(self):
        result = []
        for t in self.transformers:
            result.append(t.to_json())
        result = json.dumps(result, indent=4)
        with open(os.path.join(self.script_dir, 'local_transforms', f'{self._map_name}_local_transforms.json'), 'w') as f:
            f.write(result)
        

    def read(self):
        with open(os.path.join(self.script_dir, 'local_transforms', f'{self._map_name}_local_transforms.json'), 'r') as f:
            json_res = json.loads(f.read())
        self.transformers = []
        for t in json_res:
            self.transformers.append(Transformer(json_data=t))

    def check_transformation(self):
        local_thres = 1
        global_thres = 50

        global_coords, local_coords  = self.read_raw_points()

        for i in range(len(global_coords)):
            global_coord = global_coords[i]
            local_coord = local_coords[i]

            # Check global -> local
            new_local = self.transform_global_to_local(global_coord)
            if calculate_distance(new_local, local_coord) > local_thres:
                print(f"LOCAL THRES EXCEEDED: {global_coord} | {local_coord} | {new_local} | {local_thres}")

            # Check local -> global
            new_global = self.transform_local_to_global(local_coord)
            if calculate_distance(new_global, global_coord) > global_thres:
                print(f"GLOBL THRES EXCEEDED: {global_coord} | {local_coord} | {new_global} | {global_thres}")
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean blarg log output to create mapping of global <-> local coordinates")
    parser.add_argument('--map', type=str, default='marcadia_palace', help='Map raw log to clean')
    parser.add_argument('--debug', type=bool, default=False, help='Debug mode')

    args = parser.parse_args()
    map = args.map
    print(f"Using map: {map}")

    transform = LocalTransform(args.map)
    #transform.train(args.debug)
    transform.read()

    transform.check_transformation()