# TODO module and variable naming; how to structure 'selling_price' variable

import getpass
import json
import logging
import logging.config
import os
import sys
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
import discount
# import stir_nov as discount
import passport
import wildbrine
import pocino
import papacantella
import svd
import perfectbar
import reynaldos
import fabrique
import house
import rose
import surcharge


def enter_billing(load, price, discount_amt=0):
    try:
        edit_pricing = (
            f'{url}App_BW/staff/shipment/shipmentCostPop.aspx?loadid={load}'
        )
        browser.get(edit_pricing)

        td_list = browser.find_elements_by_tag_name('td')
        ship_cost_pos = [td.text for td in td_list].index('Shipping Costs:')
        # input box in next TD cell after Shipping Cost label
        ship_cost_cell = td_list[ship_cost_pos + 1]
        ship_cost_input = ship_cost_cell.find_element_by_tag_name('input')
        if ship_cost_input.get_attribute('value'):
            ship_cost_input.send_keys(Keys.CONTROL + 'a')
            ship_cost_input.send_keys(Keys.DELETE)
            ship_cost_input.send_keys(str(price))
            logging.info(f'{load} Base retail: {price}')
        else:
            logging(f'{load} already has existing pricing.')

        if discount_amt:
            discount.apply_discount(load, discount_amt, browser)
            logging.info(f'{load} discounted {discount_amt} ({float(discount_amt) / price})')

        save_price_btn = browser.find_element_by_id('btnUpdateCosts')
        save_price_btn.click()
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')


if len(sys.argv) < 2:
    print('Error: Expected TXT file as argument.')
    sys.exit()

continue_check = discount.verify_month()
if continue_check == False:
    sys.exit()

# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

loads_file = open(sys.argv[1], 'r')
listified = loads_file.read().strip('][').split(', ')
loadlist = [load.strip("'") for load in listified]

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into REPORT_CODE constant
# "Pricer / Discounter" report
REPORT_CODE = '23725A2291F1'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={REPORT_CODE}'
browser.get(report_url)

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in loadlist[:-1]:
    loadno.send_keys(f'\'{x}\',')
loadno.send_keys(f'\'{loadlist[-1]}\'')

# save & view report, then download
save_report_btn = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_report_btn.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(3)

# list of files in Downloads folder after downloading to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

while len(change) == 0:
    logging.info('No file downloaded.')
    after = os.listdir(DOWNLOAD_FOLDER)
    change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(f'{file_name} downloaded.')
else:
    logging.info('More than one file downloaded. Please check only one file gets downloaded.')
    sys.exit()

# output file extension is .xls but is actually.html format
filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
data = pd.read_html(filepath)
df = data[0]
load_table = df[[
    'Load #', 'Customer Name', 'Consignee', 'S/ City', 'S/ State', 'C/ City',
    'C/ State', 'C/ Zip', 'Equipment', 'Pallets', 'Weight', 'Base Retail', 
    'Cost', 'Billed', 'Customer #', 'S/ Status'
]].drop(len(df.index)-1)

# filter rows that have 0 Base Retail entered
load_table['Base Retail'] = pd.to_numeric(load_table['Base Retail'], downcast='float')
priced = load_table[load_table['Base Retail'] != 0]
print('Following loads already priced')
print(priced)
load_table = load_table[load_table['Base Retail'] == 0]
# print(load_table)

# load client info & config 
client_dict = json.load(open('db/clients.json', 'r'))
client_df_dict ={}

for key in client_dict:
    client_df_dict[key] = load_table[load_table['Customer #'] == client_dict[key]['id']]

# print(client_df_dict)

passport_df = load_table[load_table['Customer #'] == 1495]
stir_df = load_table[load_table['Customer #'] == 1374]
wildbrine_df = load_table[load_table['Customer #'] == 890]
papacantella_df = load_table[load_table['Customer #'] == 1232]
pocino_df = load_table[load_table['Customer #'] == 933]
svd_df = load_table[load_table['Customer #'] == 611]
perfectbar_df = load_table[load_table['Customer #'] == 1364]
reynaldos_df = load_table[load_table['Customer #'] == 766]
fabrique_df = load_table[load_table['Customer #'] == 1124]
house_df = load_table[load_table['Customer #'] == 1110]
rose_df = load_table[load_table['Customer #'] == 1540]
azuma_df = load_table[load_table['Customer #'] == 1301]

export_df = pd.DataFrame([['Customer Name', 'Load', 'Status', 'Destination', 'Pallets', 'Base Retail', 'Margin']])


# for key in client_df_dict:
#     client_df = client_df_dict[key]
#     if len(client_df.index) > 0:
#         client_df.reset_index(drop=True, inplace=True)
#         for row in client_df.iloc:
#             load_no = row['Load #']
#             plts = row['Pallets']
#             dest_city_state = f'{row["C/ City"]}, {row["C/ State"]}'
#             base_retail = '-'
#             margin = '-'
            
#             try:
#                 if True:
#                     max_plts = client_dict[key]['max_plts']
#                     selling_price = house.get_price(current_row)
#                     base_retail = selling_price[1]
# TODO change selling price from list to single variable, use load_no above to get load number
#                     enter_billing(*selling_price)
#                     margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
#                     logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
#                 else:
#                     logging.info(f'{str(current_load)} exceeds max weight / pallets (1650 lbs per plt or 16 pallets): {str(round(current_row["Weight"] / current_plts))} lbs per plt / {str(current_plts)} plts')
#             except Exception as e:
#                 print(e)
#                 logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

#             export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
#             export_df = pd.concat([export_df, export_row], ignore_index=False)

# TODO change order of ops to calculate retail for all first then batch enter into TMS, confirmation msg entered successfully at end

if len(passport_df.index) > 0:
    passport_df.reset_index(drop=True, inplace=True)
    for row in passport_df.index:
        current_row = passport_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = f'{current_row["C/ City"]}, {current_row["C/ State"]}'
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 20 or current_row['C/ City'] == 'Mira Loma' or current_row['C/ City'] == 'Tracy':
                selling_price = passport.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds 20 pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(stir_df.index) > 0:
    stir_df.reset_index(drop=True, inplace=True)
    for row in stir_df.index:
        current_row = stir_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = f'{current_row["C/ City"]}, {current_row["C/ State"]}'
        base_retail = '-'
        margin = '-'

        try:
            # current_row = stir_df.iloc[row]
            # TODO how to account for rates not on table? and manually entered existing?
            selling_price = discount.get_price(current_row)
            # removing costco discount
            # discount_amt = discount.get_discount(current_row, selling_price[1])
            base_retail = selling_price[1]
            enter_billing(*selling_price)
            surcharge.add_surcharge(current_load, browser, 'extreme_stir')
            margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
            logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(wildbrine_df.index) > 0:
    wildbrine_df.reset_index(drop=True, inplace=True)
    for row in wildbrine_df.index:
        current_row = wildbrine_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = f'{current_row["C/ City"]}, {current_row["C/ State"]}'
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 9:
                selling_price = wildbrine.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds 9 pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(papacantella_df.index) > 0:
    papacantella_df.reset_index(drop=True, inplace=True)
    for row in papacantella_df.index:
        current_row = papacantella_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = f'{current_row["C/ City"]}, {current_row["C/ State"]}'
        base_retail = '-'
        margin = '-'                        

        try:
            if current_plts <= 14 and (current_row['Weight'] / current_plts) <= 1650:
                selling_price = papacantella.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds max weight / pallets (1650 lbs per plt or 14 pallets): {str(round(current_row["Weight"] / current_plts))} lbs per plt / {str(current_plts)} plts')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(svd_df.index) > 0:
    svd_df.reset_index(drop=True, inplace=True)
    for row in svd_df.index:
        current_row = svd_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = f'{current_row["C/ City"]}, {current_row["C/ State"]}'
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 24 and current_row['Weight'] <= 30600:
                selling_price = svd.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds max weight or pallet (30,600 lbs / 24 plts): {str(current_row["Weight"])} lbs / {str(current_plts)} plts')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(pocino_df.index) > 0:
    pocino_df.reset_index(drop=True, inplace=True)
    for row in pocino_df.index:
        current_row = pocino_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 10:
                selling_price = pocino.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds 15 pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(perfectbar_df.index) > 0:
    perfectbar_df.reset_index(drop=True, inplace=True)
    for row in perfectbar_df.index:
        current_row = perfectbar_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 10:
                selling_price = perfectbar.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds 10 pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(reynaldos_df.index) > 0:
    reynaldos_df.reset_index(drop=True, inplace=True)
    for row in reynaldos_df.index:
        current_row = reynaldos_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 12:
                selling_price = reynaldos.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds 12 pallets: {str(current_plts)}')
        except Exception as e:
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(fabrique_df.index) > 0:
    fabrique_df.reset_index(drop=True, inplace=True)
    for row in fabrique_df.index:
        current_row = fabrique_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 3 and (current_row['Weight'] / current_plts) <= 2000:
                selling_price = fabrique.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds max weight / pallets (2000 lbs per plt or 3 pallets): {str(round(current_row["Weight"] / current_plts))} lbs per plt / {str(current_plts)} plts')
        except Exception as e:
            print(e)
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(house_df.index) > 0:
    house_df.reset_index(drop=True, inplace=True)
    for row in house_df.index:
        current_row = house_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 16 and (current_row['Weight'] / current_plts) <= 1650:
                selling_price = house.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds max weight / pallets (1650 lbs per plt or 16 pallets): {str(round(current_row["Weight"] / current_plts))} lbs per plt / {str(current_plts)} plts')
        except Exception as e:
            print(e)
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(rose_df.index) > 0:
    rose_df.reset_index(drop=True, inplace=True)
    for row in rose_df.index:
        current_row = rose_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            if current_plts <= 2 and (current_row['Weight'] / current_plts) <= 751:
                selling_price = rose.get_price(current_row)
                base_retail = selling_price[1]
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(f'{str(current_load)} {current_cs} margin: {str(margin)}, pallets: {str(current_plts)}')
            else:
                logging.info(f'{str(current_load)} exceeds max weight / pallets (751 lbs per plt or 2 pallets): {str(round(current_row["Weight"] / current_plts))} lbs per plt / {str(current_plts)} plts')
        except Exception as e:
            print(e)
            logging.info(f'{str(current_load)} errored. No rate found for {repr(e)}')

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(azuma_df.index) > 0:
    azuma_df.reset_index(drop=True, inplace=True)
    for row in azuma_df.index:
        current_row = azuma_df.iloc[row]
        load = current_row['Load #']
        try:
            edit_pricing = (f'{url}App_BW/staff/shipment/shipmentCostPop.aspx?loadid={load}')
            browser.get(edit_pricing)
            # Invoice line requires non zero number to keep line 
            surcharge.add_surcharge(load, browser, 'dedicated', 0.01)
        except Exception as e:
            logging.info(f'{load} errored. {repr(e)}')

browser.quit()
print('Browser closed.')

print('Opening log file...')
os.startfile('logs\\pricer.log')

print('Exporting summary to Excel...')
writer = pd.ExcelWriter('logs\\pricer.xlsx', engine="xlsxwriter")
export_df.to_excel(writer, sheet_name='pricer')
writer.save()
os.startfile('logs\\pricer.xlsx')

print('Done!')
