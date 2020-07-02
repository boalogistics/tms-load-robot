import json
import pandas as pd


def get_price(dfRow):
    origin = dfRow['S/ City'] + ', ' + dfRow['S/ State']
    destination = dfRow['C/ City'] + ', ' + dfRow['C/ State']
    temp = dfRow['Equipment']
    pallets = dfRow['Pallets']

    rate_table = pd.read_excel('db/passport.xlsx')
    key = json.load(open('db/equipment.json', 'r'))
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Origin', 'Temp', 'Destination'])
    retail = df.loc[origin].loc[key[temp]].loc[destination][pallets]
    return [dfRow['Load #'], retail]