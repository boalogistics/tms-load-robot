import getpass
import json
import logging
import logging.config
import os
import time
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

load_no_dict = {
    'married_loads': [],
    'indiv_loads': []
}

tms_dfs_dict = {
    'married_loads': '',
    'indiv_loads':  ''
}

# married_loads = []
# indiv_loads = []

for truck in trucks[1:]:
    if truck[1] not in load_no_dict['married_loads']:
        load_no_dict['married_loads'].append(truck[1])
    if truck[0] not in load_no_dict['indiv_loads']:
        load_no_dict['indiv_loads'].append(truck[0])

# load_nos = [married_loads, indiv_loads]

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads"


url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)


# enter report code into REPORT_CODE constant
# "Pricer / Discounter" report
REPORT_CODE = '23725A2291F1'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={REPORT_CODE}'
browser.get(report_url)

for key, value in load_no_dict.items():
    # list of files before downloading
    before = os.listdir(DOWNLOAD_FOLDER)
    
    loadlist = value

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
        # logging.info(f'{file_name} downloaded.')
    elif len(change) == 0:
        # logging.info('No file downloaded.')
        print('No file downloaded.')
    else:
        # logging.info('More than one file downloaded.')
        print('More than one file downloaded.')

    # output file extension is .xls but is actually.html format
    filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
    data = pd.read_html(filepath)
    df = data[0]
    load_table = df[[
        'Load #', 'Pallets', 'Base Cost', 'Customer #']].drop(len(df.index)-1)

    tms_dfs_dict[key] = load_table

browser.close()


tms_married_df = tms_dfs_dict['married_loads']
tms_indiv_df = tms_dfs_dict['indiv_loads']

# create master DF from Google Sheets data
gs_trucks_df = pd.DataFrame(trucks)
header = gs_trucks_df.iloc[0]
gs_trucks_df = gs_trucks_df[1:]
gs_trucks_df.columns = header
gs_trucks_df['MARRIED'] = pd.to_numeric(gs_trucks_df['MARRIED'], errors='coerce')
gs_trucks_df['TRUCK'] = pd.to_numeric(gs_trucks_df['TRUCK'], errors='coerce')
gs_trucks_df[['MARRIED', 'INDIVIDUAL', 'CHARGEABLE']] = gs_trucks_df[['MARRIED', 'INDIVIDUAL', 'CHARGEABLE']].astype(float)

gs_married_df = pd.pivot_table(gs_trucks_df[['MARRIED', 'TRUCK', 'CHARGEABLE']], index=['MARRIED', 'TRUCK'], aggfunc='sum')
gs_indiv_df = gs_trucks_df[['INDIVIDUAL', 'MARRIED', 'TRUCK', 'CHARGEABLE']]

tms_married_df['Load #'] = tms_married_df['Load #'].astype(float)

joint_indiv_df = gs_indiv_df.join(tms_indiv_df.set_index('Load #'),  on='INDIVIDUAL')
joint_married_df = gs_married_df.join(tms_married_df.set_index('Load #'), on='MARRIED').reset_index()

# compare pallet counts / totals
indiv_mismatches = joint_indiv_df[joint_indiv_df['CHARGEABLE'] != joint_indiv_df['Pallets']]
married_mismatches = joint_married_df[joint_married_df['CHARGEABLE'] != joint_married_df['Pallets']]

# get lists of mismatched master and indiv loads, create global master load list, exclude from following cost calculations
# report @ end load numbers with mismatches


# divide up total line haul cost by total pallets
joint_married_df['Per Pallet'] = joint_married_df['Base Cost'] / joint_married_df['CHARGEABLE']
per_pallet_df = joint_married_df[['MARRIED', 'Per Pallet']]

# join master truck per pallet pricing table
joint_indiv_df = joint_indiv_df.join(per_pallet_df.set_index('MARRIED'), on='MARRIED')
joint_indiv_df['Allocated Cost'] = joint_indiv_df['CHARGEABLE'] * joint_indiv_df['Per Pallet']

indiv_costs_df = joint_indiv_df[['INDIVIDUAL', 'CHARGEABLE', 'Per Pallet', 'Allocated Cost']]

print(indiv_costs_df)