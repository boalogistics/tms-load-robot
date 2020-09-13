import getpass
import json
import logging
import logging.config
import os
import pandas as pd
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tms_login as tms
from data_extract import open_sheet, create_truck

# initialize logger
# logging.config.fileConfig(fname='logs/cfg/split.conf')
# logger = logging.getLogger('')

# variables to count final results of loads
loads_dispatched = 0
loads_not_dispatched = 0

# get list of trucks from Boa Warehousing Delivery Schedule.
truck_sheet = open_sheet('Warehousing Sheet Data Feed', 'split_export')
trucks = truck_sheet.get_all_values()

married_loads = []
indiv_loads = []

for truck in trucks[1:]:
    if truck[1] not in married_loads:
        married_loads.append(truck[1])
    if truck[0] not in indiv_loads:
        indiv_loads.append(truck[0])

# # set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
# DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads"

# # list of files before downloading
# before = os.listdir(DOWNLOAD_FOLDER)

# url = 'https://boa.3plsystemscloud.com/'
# browser = tms.login(url, False)

# # enter report code into REPORT_CODE constant
# # "Pricer / Discounter" report
# REPORT_CODE = '23725A2291F1'
# report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={REPORT_CODE}'
# browser.get(report_url)

# loadlist = married_loads

# loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
# loadno.clear()
# for x in loadlist[:-1]:
#     loadno.send_keys(f'\'{x}\',')
# loadno.send_keys(f'\'{loadlist[-1]}\'')

# # save & view report, then download
# save_report_btn = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
# save_report_btn.click()
# browser.implicitly_wait(3)
# download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
# download.click()
# time.sleep(1)

# # list of files in Downloads folder after downloading to extract filename
# after = os.listdir(DOWNLOAD_FOLDER)
# change = set(after) - set(before)

# if len(change) == 1:
#     file_name = change.pop()
#     # logging.info(f'{file_name} downloaded.')
# elif len(change) == 0:
#     # logging.info('No file downloaded.')
# else:
#     # logging.info('More than one file downloaded.')

# # output file extension is .xls but is actually.html format
# filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
# data = pd.read_html(filepath)
# df = data[0]
# load_table = df[[
#     'Load #', 'Pallets', 'Base Cost', 'Customer #']].drop(len(df.index)-1)


trucks_df = pd.DataFrame(trucks)
header = trucks_df.iloc[0]
trucks_df = trucks_df[1:]
trucks_df.columns = header
trucks_df['CHARGEABLE'] = trucks_df['CHARGEABLE'].astype(float)


married_plts = pd.pivot_table(trucks_df[['MARRIED', 'CHARGEABLE']], index='MARRIED', aggfunc='sum')

print(married_plts)

# pivot table, aggregate chargeable 

# for x in trucks[1:]:
#     truck_dict = create_truck(x)
#     truck_dict_list.append(truck_dict)



# loadlist = []
# ## somewhere around here get married truck #


# for truck in truck_dict_list:
#     carrier_name = truck['carrier_name']
#     try:
#         load = [truck['load_no'], carrier_lookup[carrier_name]]
#         loadlist.append(load)
#     except:
#         logging.info('Truck # ' + truck['truck_no'] + ', Load # ' + truck['load_no'] + ', ' + carrier_name + ' is not on the carrier list.')
#         loads_not_dispatched += 1