import pandas as pd
import json

df = pd.read_csv('./note2freq.csv', sep=',')
print(df)

d = {}

for _, row in df.iterrows():
    if row['Note'].find('/') != -1:
        nlist = row['Note'].split('/')
    else:
        nlist = [row['Note']]
    for n in nlist:
        for i in range(0, 9):
            d[f'{n}{i}'] = row[str(i)]

print(json.dumps(d, sort_keys=True, indent=4))
