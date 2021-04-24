import logging
import logging.config
import time
import os
import sys
import pandas as pd
from datetime import date, datetime, timedelta
from selenium.webdriver.support.ui import Select
import tms_login as tms

if len(sys.argv) < 2:
    print('Error: Expected TXT file as argument.')
    sys.exit()

# initialize logger
print('Initializing logger...')
logging.config.fileConfig(fname='logs/cfg/book.conf')
logger = logging.getLogger('')

loads_file = open(sys.argv[1], 'r')
listified = loads_file.read().strip('][').split(', ')
loadlist = [load.strip("'") for load in listified]

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)
print('Logged into TMS.')

for x in loadlist:
    load_id = x
    load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(load_url)

    # check if load is already in booked/dispatched/cancelled status and trace priority
    status = browser.find_element_by_id('lblTitle').text.upper()

    quote_status = status.find('QUOTED') > -1   
        
    if quote_status:
        js_book = 'WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$BodyContent$lbBookShipment", "", true, "", "", false, true))'
        browser.execute_script(js_book)
        logging.info(f'{load_id} booked.')
    else:
        logging.info(f'{load_id} not booked.')        
            
    not_trace_priority = status.find('TRACE') == -1  
        
    if not_trace_priority:
        edit_shipment = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/EditShipmentPop.aspx?loadid='+load_id
        browser.get(edit_shipment)
                 

        # variable and selections for Equipment Types
        priority = Select(browser.find_element_by_id('ctl00_BodyContent_priority'))
        
        priority.select_by_value('6')
            
        # save changes
        update_btn = browser.find_element_by_css_selector('[value="Update"]')
        update_btn.click()
        logging.info(f'{load_id} marked Trace priority.')

browser.quit()
print('Browser closed.')
logging.shutdown()
print('Logger closed.')