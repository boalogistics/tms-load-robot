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
from passport import run_rates


def enterbilling(table):
    for x in table.index:
        try:
            load_id = str(table['Load #'][x])

            edit_pricing = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentCostPop.aspx?loadid='+load_id
            browser.get(edit_pricing)

            origin = table['S/ City'][x] + ', ' + table['S/ State'][x]
            destination = table['C/ City'][x] + ', ' + table['C/ State'][x]
            temp = table['Equipment'][x]
            pallets = table['Pallets'][x]

            base_retail = str(run_rates(origin, destination, pallets, temp))

            td_list = browser.find_elements_by_tag_name('td')
            shipping_cost_box_pos = [td.text for td in td_list].index('Shipping Costs:')
            # input box in next TD cell after Shipping Cost label
            shipping_cost_cell = td_list[shipping_cost_box_pos + 1]
            shipping_cost_input = shipping_cost_cell.find_element_by_tag_name('input')
            shipping_cost_input.send_keys(Keys.CONTROL + 'a')
            shipping_cost_input.send_keys(Keys.DELETE)
            shipping_cost_input.send_keys(base_retail)

            save_button = browser.find_element_by_id('btnUpdateCosts')
            save_button.click()
            logging.info(load_id + 'Origin: ' + origin + ' Destination: ' + destination + ' Pallets: ' + str(pallets) + ' Base retail: ' + base_retail)
        except Exception as e:
            logging.info(load_id + ' threw ' + repr(e))
            # exception handler for Key errors out of pallet range or city


# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = "C:\\Users\\" + getpass.getuser().title() + "\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into report_code variable
# "Pricer / Discounter" report
report_code = '23725A2291F1'
report_url = 'https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code=' + report_code
browser.get(report_url)

loadlist = ['161638', '160802', '161325', '159440', '161522', '160865', '160942', '161033']

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in loadlist[:-1]:
    loadno.send_keys('\'' + x + '\',')
loadno.send_keys('\'' + loadlist[-1] + '\'')

# save & view report, then download
save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_button.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(1)

# compares list of files in Downloads folder after downloading file to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(file_name + ' downloaded.')
elif len(change) == 0:
    logging.info('No file downloaded.')
else:
    logging.info('More than one file downloaded.')

# output file extension is .xls but is actually.html format
filepath = DOWNLOAD_FOLDER + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]
load_table = df[['Load #', 'Consignee', 'S/ City', 'S/ State', 'C/ City', 'C/ State', 'Equipment', 'Pallets', 'Base Retail', 'Customer #']].drop(len(df.index)-1)

stir = load_table[load_table['Customer #'] == 1374]
passport = load_table[load_table['Customer #'] == 1495]

if len(passport.index) > 0:
    enterbilling(passport)

if len(stir.index) > 0:
    applydiscount(stir, browser)

browser.quit()
print('Browser closed.')
# costco_discount_dict.close()

os.startfile('logs\\pricer.log')
