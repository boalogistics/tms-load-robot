import logging, logging.config
import tms_login as tms
from selenium.webdriver.support.ui import Select

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

load_list = ['159210',
'154809',
'154947',
'155852',
'156321',
'156344',
'156388',
'156572',
'157554',
'157646',
'157648',
'157822',
'157875',
'157886',
'157888',
'157892',
'157922',
'158045',
'158974',
'158975',
'158976',
'159016',
'159023',
'159051',
'159053',
'159054',
'159247',
'159344',
'159398',
'159546',
'157968'
]

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
        logging.info('POD for' + load_id + ' not uploaded: ' + repr(e))

browser.close()
print('Browser closed.')