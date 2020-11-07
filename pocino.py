import json
import pandas as pd


def get_price(df_row):
    origin = df_row['S/ City'] + ', ' + df_row['S/ State']
    destination = df_row['C/ City'] + ', ' + df_row['C/ State']

    zipcode = df_row['C/ Zip']
    pallets = df_row['Pallets']

    rate_table = pd.read_excel('db/pocino.xlsx')
    df = pd.DataFrame(rate_table)
    # df = pd.pivot_table(df, index=['Destination'])
    print(df)
    retail = df.loc[zipcode].loc[destination][pallets+1]
    return [df_row['Load #'], retail]
