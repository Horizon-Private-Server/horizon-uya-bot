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


# WRITE OUT
with open('points.json', 'w') as f:
    f.write(json.dumps(list(coords)))

