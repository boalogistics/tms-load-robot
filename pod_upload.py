import logging
import logging.config
import os
import sys
from selenium.webdriver.support.ui import Select
import tms_login as tms

# check for txt file containing load numbers as cmd line arg
if len(sys.argv) < 2:
    print('Error: Expected TXT file as argument.')
    sys.exit()

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')
logging.info('='*100)

BASE_URL = 'https://boa.3plsystemscloud.com/'
browser = tms.login(BASE_URL)

# parse string literal of list of load numbers and convert to list
loads_file = open(sys.argv[1], 'r')
listified = loads_file.read().strip('][').split(', ')
load_list = [load.strip("'") for load in listified]

PREFIX = 'ctl00_BodyContent_'

for x in load_list:
    load_id = x
    try:
        pod_path = f'S:\\POD Folder\\{load_id}.pdf'
        load_url = f'{BASE_URL}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
        browser.get(load_url)

        client_name = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCustomerInfo']/div[1]/a").text
        public_pod = client_name == 'Stir Foods LLC'

        upload = f'{BASE_URL}App_BW/staff/utilities/DocStorageAdd.aspx?loadid={load_id}'
        browser.get(upload)

        choose_file = browser.find_element_by_id(f'{PREFIX}fileUpLoadDoc')
        choose_file.send_keys(pod_path)

        if public_pod:
            view_permission = Select(browser.find_element_by_id(f'{PREFIX}rdoPermissionList'))
            view_permission.select_by_value('1')
            logging.info(f'{load_id} POD made public for {client_name}')

        upload_btn = browser.find_element_by_id(f'{PREFIX}btnUploadFile')
        upload_btn.click()
        logging.info(f'POD for {load_id} uploaded.')
    except Exception as e:
        logging.info(f'POD for {load_id} not uploaded: {repr(e)}')

logging.info('==========')
browser.close()
print('Browser closed.')

os.startfile('logs\\upload.log')
