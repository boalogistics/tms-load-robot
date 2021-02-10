import json
import logging
import logging.config
import os
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tms_login as tms
from data_extract import open_sheet, create_truck

# initialize logger
print('Initializing logger...')
logging.config.fileConfig(fname='logs/cfg/dispatch.conf')
logger = logging.getLogger('')

# constant file for emailing
exportreport = logging.FileHandler(filename='logs/dispatch_export.csv', mode='w+')
formatter = logging.Formatter()
exportreport.setFormatter(formatter)
logger.addHandler(exportreport)
print('Logger initialized.')

# variables to count final results of loads
loads_dispatched = 0
loads_not_dispatched = 0

# get list of trucks from Boa Warehousing Delivery Schedule.
truck_sheet = open_sheet('Warehousing Sheet Data Feed', 'EXPORT')
trucks = truck_sheet.get_all_values()

# populate list of dictionaries with output from Google Sheet 
truck_dict_list = []
for truck in trucks[1:]:
    truck_dict = create_truck(truck)
    truck_dict_list.append(truck_dict)

# carrier name - id # look up table in json
with open('db/carrierid.json', 'r') as f:
    carrier_lookup = json.load(f)

# get load number, truck number, and carrier name
loadlist = []
for truck in truck_dict_list:
    carrier_name = truck['carrier_name']
    try:
        load = {}
        load['id'] = truck['load_no']
        load['carrier'] = carrier_lookup[carrier_name]
        loadlist.append(load)
    except:
        logging.info(f'Truck # {truck["truck_no"]} Load # {truck["load_no"]} {carrier_name} is not on the carrier list.')
        loads_not_dispatched += 1

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

PREFIX = 'ctl00_BodyContent_'

for load in loadlist:
    load_id = load['id']
    carrier_id = load['carrier']
    load_url = f'{url}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
    logging.info(f'Opening {load_id}...')
    browser.get(load_url)

    try:
        # verify load is in booked status
        WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, 'lblTitle')))
        status = browser.find_element_by_id('lblTitle').text.upper()
        booked = status.find('BOOKED') != -1

        if booked:
            # set first window handle
            og_window = browser.window_handles[0]

            # assign carrier
            select_carrier = f'{url}App_BW/staff/shipment/selectcarriermore.aspx?loadId={load_id}'
            browser.get(select_carrier)

            WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}ListBoxCarriers')))
            carrier_select = Select(browser.find_element_by_id(f'{PREFIX}ListBoxCarriers'))
            carrier_select.select_by_value(carrier_id)

            WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}SelectCarrierSave')))
            select_carrier_btn = browser.find_element_by_id(f'{PREFIX}SelectCarrierSave')
            select_carrier_btn.click()

            # verify carrier insurance on file is not expired
            WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}ctlWarningsVertical_lblInsuranceWarnings')))
            carrier_insurance = browser.find_element_by_id(f'{PREFIX}ctlWarningsVertical_lblInsuranceWarnings').text.upper()
            carrier_insurance_expired = carrier_insurance.find('EXPIRED') != -1
            carrier_not_insured = carrier_insurance.find('not') != -1

            if carrier_insurance_expired:
                carrier_name = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCarrierInfo']/div[1]/strong").text
                logging.info(f'{load_id} not dispatched. Carrier {carrier_name}\'s insurance on file is expired.')
                loads_not_dispatched += 1
            elif carrier_not_insured:
                carrier_name = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCarrierInfo']/div[1]/strong").text
                logging.info(f'{load_id} not dispatched. Carrier {carrier_name}\ is not insured.')
                loads_not_dispatched += 1
            else:
                # dispatch
                dispatch = f'{url}App_BW/staff/operations/trackDispatchPop.aspx?loadid={load_id}'
                browser.get(dispatch)

                # variable and selections for Priority
                WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, 'btnDispatchComplete')))
                dispatch_btn = browser.find_element_by_id('btnDispatchComplete')
                dispatch_btn.click()
                # browser.switch_to.window(og_window)

                logging.info(f'Load number {load_id} dispatched!')
                loads_dispatched += 1
        else:
            logging.info(f'Auto dispatcher script did not dispatch: {status}')
            loads_not_dispatched += 1
    except Exception as e:
        logging.error(f'[{load_id} errored with exception {repr(e)}.')

browser.quit()

logging.info(f'{loads_dispatched} loads dispatched.')
logging.info(f'{loads_not_dispatched} loads not dispatched.')
print('Browser closed.')

if os.name == 'nt':
    os.startfile('logs\\dispatch.log')
