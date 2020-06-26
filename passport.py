import json
import pandas as pd

def run_rates(origin, destination, pallets, temp):
    rate_table = pd.read_excel('db/passport.xlsx')
    key = json.load(open('db/equipment.json', 'r'))
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Origin', 'Temp', 'Destination'])
    retail = df.loc[origin].loc[key[temp]].loc[destination][pallets]
    return retail