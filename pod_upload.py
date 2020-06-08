import logging, logging.config
import tms_login as tms
from selenium.webdriver.support.ui import Select

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')
logging.info('==========')

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

load_list = []

for x in load_list:
    public_pod = False
    load_id = x
    load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(load_url)
    client_name = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divCustomerInfo']/div[1]/a").text
    if client_name == 'Stir Foods LLC':
        public_pod = True
    upload = 'http://boa.3plsystemscloud.com/App_BW/staff/utilities/DocStorageAdd.aspx?loadid=' + load_id
    browser.get(upload)

    choose_file = browser.find_element_by_id('ctl00_BodyContent_fileUpLoadDoc')
    try:
        choose_file.send_keys('S:\\POD Folder\\' + load_id + '.pdf')
        if public_pod:
            view_permission = Select(browser.find_element_by_id('ctl00_BodyContent_rdoPermissionList'))
            view_permission.select_by_value('1')
            logging.info(load_id + ' POD made public for ' + client_name)

        upload_btn = browser.find_element_by_id('ctl00_BodyContent_btnUploadFile')
        upload_btn.click()
        logging.info('POD for ' + load_id + ' uploaded.')
    except Exception as e:
        logging.info('POD for ' + load_id + ' not uploaded: ' + repr(e))

browser.close()
print('Browser closed.')

import os
os.startfile('logs\\upload.log')