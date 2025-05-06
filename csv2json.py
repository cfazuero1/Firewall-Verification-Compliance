import pandas as pd

with open('gsu-contracts-out.csv', encoding='utf-8') as inputfile:
    df = pd.read_csv(inputfile, low_memory=False)

df.to_json('gsu-contracts-out1.json')