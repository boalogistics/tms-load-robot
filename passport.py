import json
import pandas as pd


def get_price(df_row):
    origin = df_row['S/ City'] + ', ' + df_row['S/ State']
    destination = df_row['C/ City'] + ', ' + df_row['C/ State']
    temp = df_row['Equipment']
    pallets = df_row['Pallets']

    rate_table = pd.read_excel('db/passport.xlsx', engine='openpyxl')
    key = json.load(open('db/equipment.json', 'r'))
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Origin', 'Temp', 'Destination'])
    retail = df.loc[origin].loc[key[temp]].loc[destination][pallets]
    return [df_row['Load #'], retail]
