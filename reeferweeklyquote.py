import getpass
import logging
import logging.config
import os
import sys
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
from data_extract import open_sheet, create_truck

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
            logging.info(f'{load} already has existing pricing.')

        save_price_btn = browser.find_element_by_id('btnUpdateCosts')
        save_price_btn.click()
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')


# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

# get list of trucks from Boa Warehousing Delivery Schedule.
pricer_sheet = open_sheet('Reefer Pricer', 'JJ')
load_info = pricer_sheet.get_all_values()

load_info_df = pd.DataFrame(load_info[1:], columns=load_info[0])
load_list = list(load_info_df['LOAD '])
print(load_list)

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
for x in load_list:
    loadno.send_keys(f'\'{x}\',')
loadno.send_keys(f'\'{load_list[-1]}\'')

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
tms_load_table = df[[
    'Load #', 'Customer Name', 'Consignee', 'S/ City', 'S/ State', 'C/ City',
    'C/ State', 'C/ Zip', 'Equipment', 'Pallets', 'Weight', 'Base Retail', 
    'Cost', 'Billed', 'Customer #', 'S/ Status'
]].drop(len(df.index)-1)

# filter rows that have 0 Base Retail entered
tms_load_table['Base Retail'] = pd.to_numeric(tms_load_table['Base Retail'], downcast='float')
priced = tms_load_table[tms_load_table['Base Retail'] != 0]
print('Following loads already priced')
print(priced)
tms_load_table = tms_load_table[tms_load_table['Base Retail'] == 0]
print(tms_load_table)

export_df = pd.DataFrame([[
    'Customer Name', 'Load', 'Status', 'Destination',
    'Pallets', 'Base Retail', 'Margin'
]])

# cast weight, pallet to float
# cast load# to integer to match tms_load_table index
tms_load_table.index = list(tms_load_table['Load #'])
tms_load_table['Pallets'] = pd.to_numeric(tms_load_table['Pallets'], downcast='float')
tms_load_table['Weight'] = pd.to_numeric(tms_load_table['Weight'], downcast='float')
load_info_df['LOAD '] = pd.to_numeric(load_info_df['LOAD '], downcast='integer')
load_info_df['PLTS'] = pd.to_numeric(load_info_df['PLTS'], downcast='float')
load_info_df['Weight'] = pd.to_numeric(load_info_df['Weight'], downcast='float')

for row in load_info_df.iloc:   
    load = row['LOAD ']

    try:
        city_match = tms_load_table.loc[load]['C/ City'] == row['Destination']
        state_match = tms_load_table.loc[load]['C/ State'] == row['State']
        plts_match = tms_load_table.loc[load]['Pallets'] == row['PLTS']
        wt_match = tms_load_table.loc[load]['Weight'] == row['Weight']
    except KeyError:
        logging.error(f'{load} not in TMS DataFrame.')

    if city_match and state_match and plts_match and wt_match:
        # enter_billing(load, row['Cost'])
        print(load, row['Cost'])
    else:
        logging.info(f'Load {load} has mismatched information.')

    # TODO incorporate client/cost/margin after fleshed out
    # export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_row['S/ Status'], current_cs, current_plts, base_retail, margin]])
    export_row = pd.DataFrame([[
        'n/a', 
        load, 
        tms_load_table.loc[load]['S/ Status'], 
        row['Destination'] + ', ' + row['State'], 
        row['PLTS'], 
        row['Cost'], 
        'n/a'
    ]])
    export_df = pd.concat([export_df, export_row], ignore_index=False)
    print(export_df)

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
