
from utils.utils import *

x = '020001396D0267BCA8433B0CBD4300E0074200A08238008075B800B906C0'

for start_idx in [0,1]:
    print("===========================")
    print(start_idx)
    d = x[start_idx:]
    while start_idx + 4 < len(d):
        this = d[start_idx:start_idx+4]
        print(this, hex_to_int_little(this))
        start_idx += 4
