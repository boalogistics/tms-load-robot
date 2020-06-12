import pandas as pd

def run_rates(origin, destination, pallets):
    rate_table = pd.read_excel('db/passport.xlsx')
    df = pd.DataFrame(rate_table)
    df = pd.pivot_table(df, index=['Origin', 'Destination'])
    retail = df.loc['Kent, WA'].loc['Ankeny, IA'][5]
    return retail