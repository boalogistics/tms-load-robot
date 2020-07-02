# TODO refactor enterbilling() and see how to modularize passport module

import getpass
import logging
import logging.config
import os
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
from discount import applydiscount
import passport, stir


def enter_billing(load, price, discount=0):
    url = 'http://boa.3plsystemscloud.com/'
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
        ship_cost_input.send_keys(Keys.CONTROL + 'a')
        ship_cost_input.send_keys(Keys.DELETE)
        ship_cost_input.send_keys(price)

        if discount:
            applydiscount()

        save_button = browser.find_element_by_id('btnUpdateCosts')
        save_button.click()
        logging.info(f'{load} Base retail: {price}')
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')


# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

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

loadlist = [
    '161638', '160802', '161325',
    '159440', '161522', '160865',
    '160942', '161033'
    ]

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in loadlist[:-1]:
    loadno.send_keys(f'\'{x}\',')
loadno.send_keys(f'\'{loadlist[-1]}\'')

# save & view report, then download
save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_button.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(1)

# list of files in Downloads folder after downloading to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(f'{file_name} downloaded.')
elif len(change) == 0:
    logging.info('No file downloaded.')
else:
    logging.info('More than one file downloaded.')

# output file extension is .xls but is actually.html format
filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
data = pd.read_html(filepath)
df = data[0]
load_table = df[[
    'Load #', 'Consignee', 'S/ City', 'S/ State', 'C/ City',
    'C/ State', 'Equipment', 'Pallets', 'Base Retail', 'Customer #'
    ]].drop(len(df.index)-1)

passport_df = load_table[load_table['Customer #'] == 1495][]
stir_df = load_table[load_table['Customer #'] == 1374]

if len(passport_df.index) > 0:
    for row in passport_df.index: 
        selling_price = passport.get_price(passport_df.iloc[row])
        enter_billing(passport_df.iloc[row].loc['Load #'], selling_price)

if len(stir_df.index) > 0:
    for row_dict in stir_df.to_dict(orient='records'): 
        selling_price = stir.get_price(stir_df.iloc[row])
        applydiscount(stir_df.iloc[row], selling_price, browser)


browser.quit()
print('Browser closed.')

os.startfile('logs\\pricer.log')
