import logging
import logging.config
import os
from selenium.webdriver.support.ui import Select
import tms_login as tms

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')
logging.info('==========')

BASE_URL = 'https://boa.3plsystemscloud.com/'
browser = tms.login(BASE_URL)

load_list = []

prefix = 'ctl00_BodyContent_'

for x in load_list:
    public_pod = False
    load_id = x
    load_url = f'{BASE_URL}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
    browser.get(load_url)
    client_name = browser.find_element_by_xpath(f"//div[@id='{prefix}divCustomerInfo']/div[1]/a").text
    if client_name == 'Stir Foods LLC':
        public_pod = True
    upload = f'{BASE_URL}App_BW/staff/utilities/DocStorageAdd.aspx?loadid={load_id}'
    browser.get(upload)

    choose_file = browser.find_element_by_id(f'{prefix}fileUpLoadDoc')
    try:
        choose_file.send_keys(f'S:\\POD Folder\\{load_id}.pdf')
        if public_pod:
            view_permission = Select(browser.find_element_by_id(f'{prefix}rdoPermissionList'))
            view_permission.select_by_value('1')
            logging.info(load_id + ' POD made public for ' + client_name)

        upload_btn = browser.find_element_by_id(f'{prefix}btnUploadFile')
        upload_btn.click()
        logging.info(f'POD for {load_id} uploaded.')
    except Exception as e:
        logging.info(f'POD for {load_id} not uploaded: {repr(e)}')

browser.close()
print('Browser closed.')

os.startfile('logs\\upload.log')
