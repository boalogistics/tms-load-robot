# TODO module and variable naming; how to structure 'selling_price' variable

import getpass
import logging
import logging.config
import os
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
# import discount
import discount_sept as discount
import passport


def enter_billing(load, price, discount_amt=0):
    # url = 'http://boa.3plsystemscloud.com/'
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

loadlist = ['169350']

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
    'C/ State', 'Equipment', 'Pallets', 'Weight', 'Base Retail', 'Customer #'
    ]].drop(len(df.index)-1)

passport_df = load_table[load_table['Customer #'] == 1495]
stir_df = load_table[load_table['Customer #'] == 1374]

if len(passport_df.index) > 0:
    passport_df.reset_index(drop=True, inplace=True)
    for row in passport_df.index:
        try:
            current_row = passport_df.iloc[row]
            if current_row['Pallets'] < 21 or current_row['C/ City'] == 'Mira Loma':
                selling_price = passport.get_price(current_row)
                enter_billing(*selling_price)
            else:
                logging.info(str(current_row['Load #']) + ' exceeds 20 pallets')
        except Exception as e:
            logging.info(str(current_row['Load #']) +  ' errored. ' + repr(e))

if len(stir_df.index) > 0:
    stir_df.reset_index(drop=True, inplace=True)
    for row in stir_df.index:
        try:
            current_row = stir_df.iloc[row]
            # TODO how to account for rates not on table? and manually entered existing?
            # check if Base Retail == 0
            selling_price = discount.get_price(current_row)
            discount_amt = discount.get_discount(current_row, selling_price[1])
            enter_billing(*selling_price, discount_amt)
            # print(*selling_price, discount_amt)
        except Exception as e:
            logging.info(str(current_row['Load #']) +  ' errored. ' + repr(e))

browser.quit()
print('Browser closed.')

os.startfile('logs\\pricer.log')
