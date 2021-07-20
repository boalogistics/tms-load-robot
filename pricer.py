import getpass
import json
import logging
import logging.config
import os
import re
import sys
import time
from math import ceil
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import tms_login as tms

SURCHARGE_CLIENTS = [] # Pasta Piccinini = 817


# TODO REFACTOR ENTER BILLING & SURCHARGE TOGETHER?
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

        # if discount_amt:
        #     discount.apply_discount(load, discount_amt, browser)
        #     logging.info(f'{load} discounted {discount_amt} ({float(discount_amt) / price})')

        save_price_btn = browser.find_element_by_id('btnUpdateCosts')
        save_price_btn.click()
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')


def add_surcharge(load, charge, surcharge_amt):
    surcharge_type = {
        'additional': ['Additional Surcharge:', '295'],
        'dedicated': ['Dedicated Truck:', '241'],
        'extreme': ['Extreme Weather:','298']
    }
    
    surcharge = surcharge_type[charge]

    try:
        edit_pricing = (
            f'{url}App_BW/staff/shipment/shipmentCostPop.aspx?loadid={load}'
        )
        browser.get(edit_pricing)

        td_list = browser.find_elements_by_tag_name('td')
        surcharge_exists = any(td.text == surcharge[0] for td in td_list)
        while not surcharge_exists:
            supplemental_select = Select(browser.find_element_by_id('ddlAddSupplementals'))
            try:
                supplemental_select.select_by_value(surcharge[1])
            except Exception as e:
                logging.exception(f'{load} threw {repr(e)}')
            add_button = browser.find_element_by_id('btnAddSupplemental')
            add_button.click()
            logging.info(f'Added invoice line {surcharge[0]}')
            td_list = browser.find_elements_by_tag_name('td')
            surcharge_exists = any(td.text == surcharge[0] for td in td_list)

        surcharge_box_pos = [td.text for td in td_list].index(surcharge[0])
        # input box in next TD cell after {SURCHARGE} label
        surcharge_cell = td_list[surcharge_box_pos + 1]
        surcharge_input = surcharge_cell.find_element_by_tag_name('input')
        surcharge_input.send_keys(Keys.CONTROL + 'a')
        surcharge_input.send_keys(Keys.DELETE)
        surcharge_input.send_keys(str(surcharge_amt))
        logging.info(f'{load} additional surcharge {surcharge[0]} {surcharge_amt}')

        save_price_btn = browser.find_element_by_id('btnUpdateCosts')
        save_price_btn.click()
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')

def calc_wt_sc(baseprice, weight, pallets):
    # Max weight to count as 1 chargeable pallet
    MAX_WEIGHT = 1768
    # Pallets exceeding will count as 2 chargeable plts
    MAX_WEIGHT_2 = 2350
    # Percent discount for pallet counts 1 to 10
    discount_rates = [
        0.006, 0.0075, 0.0035, 0.0035, 0.0040,
        0.0045, 0.005, 0.0055, 0.006, 0.006
    ]
    
    wt_per_plt = weight / pallets

    if wt_per_plt <= MAX_WEIGHT:
        chgble_plt = 1
    elif wt_per_plt > MAX_WEIGHT_2:
        chgble_plt = 2
    else:
        chgble_plt = wt_per_plt / MAX_WEIGHT

    discount = discount_rates[pallets - 1]
    chargeable_selling = (chgble_plt * baseprice) * (1 - discount)

    if baseprice > chargeable_selling:
        return baseprice
    else:
        if pallets < 5:
            return ceil((chargeable_selling - 5) / 10) * 10
        else:
            return ceil((chargeable_selling / 10)) * 10


def get_price(df_row, client):
    '''Master function with all included
    '''
    rate_table = pd.read_excel(f'db/{client}.xlsx', engine='openpyxl')
    df = pd.DataFrame(rate_table)
    pallets = df_row['Pallets']
    origin = f'{df_row["S/ City"]}, {df_row["S/ State"]}'
    
    # Check if destination zip code required
    regex_nums = re.findall('[0-9]', rate_table['Destination'][0])
    if len(regex_nums) > 0:
        destination = f'{df_row["C/ City"]}, {df_row["C/ State"]} {str(int(df_row["C/ Zip"])).zfill(5)}'
    else:
        destination = f'{df_row["C/ City"]}, {df_row["C/ State"]}'

    # special cases for specific clients    
    if client == 'passport':
        temp = df_row['Equipment']
        key = json.load(open('db/equipment.json', 'r'))
        df = pd.pivot_table(df, index=['Origin', 'Temp', 'Destination'])
        retail = df.loc[origin].loc[key[temp]].loc[destination][pallets]
    elif client == 'stir':
        weight = df_row['Weight']
        key = json.load(open('db/region.json', 'r'))
        df = pd.pivot_table(df, index=['Origin', 'Destination'])
        base_selling = df.loc[key[origin]].loc[destination][pallets]
        retail = calc_wt_sc(base_selling, weight, pallets)        
    elif client == 'perfectbar'or client =='westerntrans':
        df = pd.pivot_table(df, index=['Origin', 'Destination'])
        retail = df.loc[origin].loc[destination][pallets]

    # standard default lookup
    else:
        df = pd.pivot_table(df, index=['Destination'])
        retail = df.loc[destination][pallets]

    return retail


if len(sys.argv) < 2:
    print('Error: Expected TXT file as argument.')
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
time.sleep(5)

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
# TODO COMBINE DF AND MAIN CLIENT DICTS

# for key in client_dict:
#     client_dict[key]['loads'] = load_table[load_table['Customer #'] == client_dict[key]['id']]

# print(client_dict)

export_df = pd.DataFrame([[
    'Customer Name', 'Load', 'Status', 
    'Destination', 'Pallets', 'Base Retail', 'Margin'
]])

# TODO change order of ops to calculate retail for all first then batch enter into TMS, confirmation msg entered successfully at end

for client_name in client_df_dict:
    client_df = client_df_dict[client_name]
    if len(client_df.index) > 0:
        client_df.reset_index(drop=True, inplace=True)
        for row in client_df.iloc:
            client_id = client_dict[client_name]['id']
            load_no = row['Load #']
            plts = row['Pallets']
            weight = row['Weight']
            dest_city = row['C/ City']
            dest_city_state = f'{dest_city}, {row["C/ State"]}'
            base_retail = '-'
            margin = '-'
            

            # TODO SIMPLFIY CLIENT CHOICE AND SELLING/BASERETAIL/MARGIN LOGIC
            try:
                # Azuma - only enter blank Dedicated surcharge line
                if client_id == 1301:
                    logging.info('Azuma dedicated line')
                    add_surcharge(load_no, 'dedicated', 0.01)
                # House Foods & Passort - ignore pallet limit for FTL locations
                elif (client_id == 1495 or client_id == 1110) and (dest_city in client_dict[client_name]['ftl_dests']):
                    selling_price = get_price(row, client_name)
                    base_retail = selling_price
                    enter_billing(load_no, selling_price)
                    margin = (row['Billed'] + selling_price - row['Cost']) / (row['Billed'] + selling_price)
                    logging.info(f'{str(load_no)} {dest_city_state} margin: {str(margin)}, pallets: {str(plts)}')
                else:
                    client_attribs = client_dict[client_name]
                    max_keys = ['max_plts', 'max_wt', 'max_wt_pp']
                    has_max = any(key in client_attribs for key in max_keys)
                    exceeds_plts, exceeds_wt, exceeds_wt_pp = False, False, False
                    max_plts, max_wt, max_wt_pp = 'n/a', 'n/a', 'n/a'

                    if has_max:
                        if 'max_plts' in client_attribs:
                            max_plts = client_attribs['max_plts']
                            exceeds_plts = plts > max_plts
                        if 'max_wt' in client_attribs:
                            max_wt = client_attribs['max_wt']
                            exceeds_wt = weight > max_wt
                        if 'max_wt_pp' in client_attribs:
                            max_wt_pp = client_attribs['max_wt_pp']
                            exceeds_wt_pp = (weight / plts) > max_wt_pp

                    if any([exceeds_plts, exceeds_wt, exceeds_wt_pp]):
                        # TODO check to see if method similar to SURCHARGE CLIENTS will work
                        logging.info(f'{str(load_no)} exceeds one or more maximums: ')
                        logging.info(f'  Max weight per plt: {max_wt_pp} lbs / {str(round(weight / plts))} lbs;')
                        logging.info(f'  Max plts: {max_plts} plts / {str(plts)} plts;')
                        logging.info(f'  Max total weight: {max_wt} lbs / {str(weight)} lbs')
                        
                        # Additional Surcharge // $0.01 if base retail 0
                        if client_id in SURCHARGE_CLIENTS:
                            surcharge_price = 0.01
                            add_surcharge(load_no, 'additional', surcharge_price)
                    # SPECIAL CASE FOR FTL LEGACY FARMS
                    elif client_name == 'legacyfarms':
                        # REJECT IF COST IS OVER STD $385
                        if row['Cost'] > 385:
                            logging.info(f'Cost exceeds 385.00: {row["Cost"]}')
                        else:
                            selling_price = get_price(row, client_name)
                            base_retail = selling_price
                            enter_billing(load_no, selling_price)
                            margin = (row['Billed'] + selling_price - row['Cost']) / (row['Billed'] + selling_price)
                            logging.info(f'{str(load_no)} {dest_city_state} margin: {str(margin)}, pallets: {str(plts)}')
                    else:
                        selling_price = get_price(row, client_name)
                        base_retail = selling_price
                        enter_billing(load_no, selling_price)

                        if client_id in SURCHARGE_CLIENTS:
                            surcharge_pct = client_attribs['surcharge_pct']
                            surcharge_price = selling_price * surcharge_pct
                            add_surcharge(load_no, 'additional', surcharge_price)
                            selling_price = selling_price + surcharge_price
                        
                        margin = (row['Billed'] + selling_price - row['Cost']) / (row['Billed'] + selling_price)
                        logging.info(f'{str(load_no)} {dest_city_state} margin: {str(margin)}, pallets: {str(plts)}')
            except Exception as e:
                    logging.exception(f'{str(load_no)} errored. No rate for {repr(e)}')

            export_row = pd.DataFrame([[
                row['Customer Name'], load_no, row['S/ Status'], 
                dest_city_state, plts, base_retail, margin
            ]])
            export_df = pd.concat([export_df, export_row], ignore_index=False)

browser.quit()
print('Browser closed.')

print('Opening log file...')
os.startfile('logs\\pricer.log')

print('Exporting summary to Excel...')
writer = pd.ExcelWriter('logs\\pricer.xlsx', engine="xlsxwriter")
export_df.to_excel(writer, sheet_name='pricer', index=False)
writer.save()
os.startfile('logs\\pricer.xlsx')

print('Done!')
