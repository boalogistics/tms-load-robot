# TODO module and variable naming; how to structure 'selling_price' variable

import getpass
import logging
import logging.config
import os
import sys
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
import discount
# import discount_sept as discount
import passport
import wildbrine
# import pocino
import papacantella
import svd


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


if len(sys.argv) < 2:
    print('Error: Expected TXT file as argument.')
    sys.exit()
    
# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

loads_file = open(sys.argv[1], 'r')
listified = loads_file.read().strip('][').split(', ')
loadlist = [load.strip("'") for load in listified]

# # set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
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
# filepath = 'Pricer_Discounter20201106.xls'
data = pd.read_html(filepath)
df = data[0]
load_table = df[[
    'Load #', 'Customer Name', 'Consignee', 'S/ City', 'S/ State', 'C/ City',
    'C/ State', 'C/ Zip', 'Equipment', 'Pallets', 'Weight', 'Base Retail', 'Cost', 'Billed', 'Customer #'
    ]].drop(len(df.index)-1)

# filter rows that have 0 Base Retail entered
load_table['Base Retail'] = pd.to_numeric(load_table['Base Retail'], downcast='float')
priced = load_table[load_table['Base Retail'] != 0]
print('Following loads already priced')
print(priced)
load_table = load_table[load_table['Base Retail'] == 0]
print(load_table)

# TODO store client name + id in json
passport_df = load_table[load_table['Customer #'] == 1495]
stir_df = load_table[load_table['Customer #'] == 1374]
wildbrine_df = load_table[load_table['Customer #'] == 890]
papacantella_df = load_table[load_table['Customer #'] == 1232]
pocino_df = load_table[load_table['Customer #'] == 933]
svd_df = load_table[load_table['Customer #'] == 611]

export_df = pd.DataFrame([['Customer Name', 'Load', 'City-State', 'Pallets', 'Base Retail', 'Margin']])

if len(passport_df.index) > 0:
    passport_df.reset_index(drop=True, inplace=True)
    for row in passport_df.index:
        current_row = passport_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 21 or current_row['C/ City'] == 'Mira Loma' or current_row['C/ City'] == 'Tracy':
                selling_price = passport.get_price(current_row)
                base_retail = selling_price[1]
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 20 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)
        
if len(stir_df.index) > 0:
    stir_df.reset_index(drop=True, inplace=True)
    for row in stir_df.index:
        current_row = stir_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        try:
            current_row = stir_df.iloc[row]
            # TODO how to account for rates not on table? and manually entered existing?
            # check if Base Retail == 0
            selling_price = discount.get_price(current_row)
            discount_amt = discount.get_discount(current_row, selling_price[1])
            base_retail = selling_price[1]
            # enter_billing(*selling_price, discount_amt)
            margin = (current_row['Billed'] + selling_price[1] - current_row['Cost'] + discount_amt) / (current_row['Billed'] + selling_price[1])
            logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            # print(*selling_price, discount_amt)
        except Exception as e:
            logging.info(str(current_row['Load #']) +  ' errored. No rate found for ' + repr(e))

        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(wildbrine_df.index) > 0:
    wildbrine_df.reset_index(drop=True, inplace=True)
    for row in wildbrine_df.index:
        current_row = wildbrine_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 10:
                selling_price = wildbrine.get_price(current_row)
                base_retail = selling_price[1]
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 9 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(papacantella_df.index) > 0:
    papacantella_df.reset_index(drop=True, inplace=True)
    for row in papacantella_df.index:
        current_row = papacantella_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 15:
                selling_price = papacantella.get_price(current_row)
                base_retail = selling_price[1]
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 14 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(svd_df.index) > 0:
    svd_df.reset_index(drop=True, inplace=True)
    for row in svd_df.index:
        current_row = svd_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        base_retail = '-'
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 24 and current_row['Weight'] <= 30600:
                selling_price = svd.get_price(current_row)
                base_retail = selling_price[1]
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds max weight / pallet (30,600 / 24): ' + str(current_row['Weight']) + ' / ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_row['Customer Name'], current_load, current_cs, current_plts, base_retail, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

# if len(pocino_df.index) > 0:
#     # pocino_df.reset_index(drop=True, inplace=True)
#     for row in pocino_df.index:
#         current_row = pocino_df.iloc[row]
#         current_load = current_row['Load #']
#         current_plts = current_row['Pallets']
#         # current_retail = current_row['Base Retail']
#         current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
#         selling_price =['-', '-']
#         margin = '-'

#         # if current_retail != 0.0:    
#         try:
#             if current_plts < 16:
#                 selling_price = pocino.get_price(current_row)
#                 # enter_billing(*selling_price)
#                 margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
#                 logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
#             else:
#                 logging.info(str(current_load) + ' exceeds 15 pallets: ' + str(current_plts))
#         except Exception as e:
#             logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
#         # else:
#         #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
#         export_row = pd.DataFrame([[current_load, current_cs, current_plts, selling_price[1], margin]])
#         export_df = pd.concat([export_df, export_row], ignore_index=False)

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