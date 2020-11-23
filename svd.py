import json
import pandas as pd


def get_price(df_row):
    destination = df_row['C/ City'] + ', ' + df_row['C/ State']
    pallets = df_row['Pallets']

    rate_table = pd.read_excel('db/svd.xlsx')
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Destination'])
    retail = df.loc[destination][pallets]
    return [df_row['Load #'], retail]