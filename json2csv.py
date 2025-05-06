import pandas as pd

with open('gsu-contracts-out1.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('gsu-contracts-out1.csv', encoding='utf-8', index=False)