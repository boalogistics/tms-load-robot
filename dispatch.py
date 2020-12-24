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

truck_dict_list = []

for x in trucks[1:]:
    truck_dict = create_truck(x)
    truck_dict_list.append(truck_dict)

# carrier name - id # look up table in json
with open('db/carrierid.json', 'r') as f:
    carrier_lookup = json.load(f)

loadlist = []

for truck in truck_dict_list:
    carrier_name = truck['carrier_name']
    try:
        load = [truck['load_no'], carrier_lookup[carrier_name]]
        loadlist.append(load)
    except:
        logging.info('Truck # ' + truck['truck_no'] + ', Load # ' + truck['load_no'] + ', ' + carrier_name + ' is not on the carrier list.')
        loads_not_dispatched += 1

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

PREFIX = 'ctl00_BodyContent_'

for x in loadlist:
    load_id = x[0]
    carrier_id = x[1]
    load_url = f'{url}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
    browser.get(load_url)

    # verify load is in booked status
    status = browser.find_element_by_id('lblTitle').text.upper()
    booked = status.find('BOOKED') != -1

    if booked:
        # set first window handle
        og_window = browser.window_handles[0]

        # assign carrier
        vol_carrier_link = browser.find_element_by_id(f'{PREFIX}hlCarrierVolLink')
        vol_carrier_link.click()
        carrier_select = Select(browser.find_element_by_id(f'{PREFIX}ListBoxCarriers'))
        carrier_select.select_by_value(carrier_id)
        select_carrier_btn = browser.find_element_by_id(f'{PREFIX}SelectCarrierSave')
        select_carrier_btn.click()
        WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}ctlWarningsVertical_lblInsuranceWarnings')))

        # verify carrier insurance on file is not expired
        carrier_insurance = browser.find_element_by_id(f'{PREFIX}ctlWarningsVertical_lblInsuranceWarnings').text.upper()
        carrier_insurance_expired = carrier_insurance.find('EXPIRED') != -1

        if carrier_insurance_expired:
            carrier_name = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCarrierInfo']/div[1]/strong").text
            logging.info(load_id + ' not dispatched. Carrier {}\'s insurance on file is expired.'.format(carrier_name))
            loads_not_dispatched += 1
        else:
            # dispatch
            # dispatch = 'http://boa.3plsystemscloud.com/App_BW/staff/operations/trackDispatchPop.aspx?loadid='+load_id
            # browser.get(dispatch)
            dispatch_link = browser.find_element_by_id(f'{PREFIX}lbDispatchLink')
            dispatch_link.click()
            WebDriverWait(browser, timeout=30).until(EC.number_of_windows_to_be(2))

            # set handle to popup and switches to popup
            popup = browser.window_handles[1]
            browser.switch_to.window(popup)

            # variable and selections for Priority
            dispatch_btn = browser.find_element_by_id('btnDispatchComplete')
            dispatch_btn.click()
            browser.switch_to.window(og_window)

            logging.info(f'Load number {load_id} dispatched!')
            loads_dispatched += 1
    else:
        logging.info(f'Auto dispatcher script did not dispatch: {status}')
        loads_not_dispatched += 1

browser.quit()

logging.info(f'{loads_dispatched} loads dispatched.')
logging.info(f'{loads_not_dispatched} loads not dispatched.')
print('Browser closed.')

if os.name == 'nt':
    os.startfile('logs\\dispatch.log')
