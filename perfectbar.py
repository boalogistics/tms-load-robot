import json
import pandas as pd


def get_price(df_row):
    destination = df_row['C/ City'] + ', ' + df_row['C/ State'] + ' ' + str(int(df_row['C/ Zip'])).zfill(5)

    pallets = df_row['Pallets']

    rate_table = pd.read_excel('db/perfectbar.xlsx', engine='openpyxl')
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Destination'])
    retail = df.loc[destination][pallets]
    return [df_row['Load #'], retail]
