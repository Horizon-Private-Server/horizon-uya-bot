import pandas as pd
from collections import defaultdict

df = pd.read_csv('../profiles.csv')

d = defaultdict(list)

for _, row in df.iterrows():
	d[row['overall_skill']].append(row['profile'])



for k in d.keys():
	res = ', '.join([str(s) for s in list(d[k])])
	print(f"profileDifficulty[{k}] = new HashSet<int> {{ {res} }};")

