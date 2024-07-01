import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import json


mapping = [
    [0, 0],
    [216, 0],
    [217, .19],
    [336, .31],
    [421, .43],
    [583, .59],
    [639, .68],
    [742, .79],
    [826, .89],
    [985, .98],
    [1047, 1.16],
    [1242, 1.43],
    [1396, 1.53],
    [1599, 1.74],
    [1834, 1.93],
    [2147, 2.28],
    [2293, 2.48],
    [2550, 2.78],
    [2814, 3.11],
]

# Convert mapping to numpy arrays
x, y = zip(*mapping)
x = np.array(x)
y = np.array(y)

# Create interpolation function
interp_func = interp1d(x, y, kind='linear', fill_value='extrapolate')

# Generate numpy array of length 2814
result_array = interp_func(np.arange(1, 2815))

print(result_array)

final_result = {

}

for i in range(len(result_array)):
    final_result[str(i)] = float(result_array[i])

s = json.dumps(final_result, indent=4)
with open('grav_dist_to_time.json', 'w') as f:
    f.write(s)