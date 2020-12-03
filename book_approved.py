import logging
import logging.config
import time
import os
import pandas as pd
from selenium import webdriver
from datetime import date, datetime, timedelta
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tms_login as tms

# initialize logger
print('Initializing logger...')
logging.config.fileConfig(fname='logs/cfg/book.conf')
logger = logging.getLogger('')

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)
print('Logged into TMS.')

load_list = ['175899', '176308', '176309', '176310', '176311', '176312', '176313', '176314', '176315', '176316', '176317', '176400', '176401', '176402', '176403', '176404', '176616', '176618', '176681', '176682', '176683', '176684', '176781', '176782', '176783', '176784', '176785', '176786', '176787', '176788']


for x in load_list:
    load_id = x
    load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(load_url)

    # check if load is already in booked/dispatched/cancelled status and trace priority
    status = browser.find_element_by_id('lblTitle').text.upper()

    quote_status = status.find('QUOTED') > -1   
        
    if quote_status:
        js_book = 'WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$BodyContent$lbBookShipment", "", true, "", "", false, true))'
        browser.execute_script(js_book)
        print(f'{load_id} booked.')
    else:
        print(f'{load_id} not booked.')        
            
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

browser.quit()
