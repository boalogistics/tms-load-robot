## TODO add error catcher for timing out and/or alert on LCR page to skip current load number
## alternatively add parameter for webdrvr options in tms_login


import csv
# import tms_login as tms
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

# activate chrome driver
browser = webdriver.Chrome()
browser.implicitly_wait(3)
browser.maximize_window()
browser.get('https://boa.3plsystemscloud.com/')

# page elements to login
boa_user = browser.find_element_by_id('txb-username')
boa_pw = browser.find_element_by_id('txb-password')
login_button = browser.find_element_by_id('ctl00_ContentBody_butLogin')

# login credentials
boa_user.send_keys('***EMAIL HERE***')
boa_pw.send_keys('***PASSWORD HERE***')
login_button.click()

# put FOR loop here to loop through list of load numbers
loadlist = ['153110', 
'153401', 
'153219', 
'152872', 
'153218', 
'153702', 
'152874', 
'153274', 
'153257', 
'153029', 
'154072', 
'153023', 
'152903', 
'153313', 
'152956', 
'153383', 
'153369', 
'154099', 
'153085', 
'153748', 
'153020'
]

for x in loadlist:
    load_id = x
    url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(url)

    # assign carrier
    lcr_carrier_link = browser.find_element_by_id('ctl00_BodyContent_hlCarrierLCRLink')
    lcr_carrier_link.click()
   
    # volume carrier only check
    volume_only = len(browser.find_elements(By.ID, 'ctl00_BodyContent_LineVolumeDiv'))
   
    if volume_only:
        print(load_id + ' is volume only')
    else:
        # wait until the rate table populates and becomes clickable
        WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_objRateEngine_gvRates_ctl02_lnkQuoteNow')))

        # carrier filter logic
        rows = browser.find_elements_by_css_selector('tr.select-tooltip')
        buttons = browser.find_elements_by_css_selector('a.button-link')

        button_index = ''

        for y in rows:
            row_index = rows.index(y)
            carrier_name = rows[row_index].get_attribute('title')
            
            # carrier filters; if enabling or disabling, modify IF block below
            tradeshow_check = carrier_name.lower().find('trade show') < 0
            frontline_check = carrier_name.lower().find('frontline') < 0
            clearlane_check = carrier_name.lower().find('clear lane') < 0
            overnite_check = carrier_name.lower().find('best overnite') < 0
            custom_check = carrier_name.lower().find('custom companies') < 0
            roadrunner_check = carrier_name.lower().find('roadrunner') < 0
            central_check = carrier_name.lower().find('central freight') < 0
            
            if tradeshow_check and frontline_check and clearlane_check and overnite_check and custom_check and roadrunner_check and central_check:
                button_index = row_index * 2
                break 

        buttons[button_index].click()
        WebDriverWait(browser, timeout=30).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_divCarrierInfo')))
        carrier_info = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divCarrierInfo']/div[1]/strong").text

        print(load_id)
        print(carrier_info)
        with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
            carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            carrier_writer.writerow([load_id, carrier_info])
