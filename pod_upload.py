import logging, logging.config
import tms_login as tms
from selenium.webdriver.support.ui import Select

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')
logging.info('==========')

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

load_list = ['159585',
'154601',
'154969',
'155714',
'155822',
'155864',
'155964',
'156005',
'156065',
'156080',
'156081',
'156083',
'156104',
'156213',
'156250',
'156284',
'156294',
'156308',
'156364',
'156368',
'156427',
'156434',
'156438',
'156536',
'156537',
'156562',
'156563',
'156565',
'156567',
'156591',
'156596',
'156608',
'156615',
'156624',
'157552',
'157556',
'157565',
'157570',
'157576',
'157617',
'157642',
'157814',
'157858',
'157873',
'157935',
'158043',
'158046',
'158077',
'158844',
'158854',
'158870',
'158907',
'158941',
'158943',
'158972',
'158981',
'159000',
'159018',
'159099',
'159114',
'159140',
'159157',
'159160',
'159198',
'159268',
'155919',
'155961',
'156076',
'156188',
'156609',
'157881',
'157926',
'158056',
'158066',
'159103',
'159140',
'159159',
'159174']

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