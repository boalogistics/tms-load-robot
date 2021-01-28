## TODO add code to handle alert on LCR and Edit profile window

import csv
import tms_login as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

baseurl = 'https://boa.3plsystemscloud.com/'
browser = tms.login(baseurl, False)

PREFIX = 'ctl00_BodyContent_'

# put FOR loop here to loop through list of load numbers
loadlist = []

for x in loadlist:
    try:
        load_id = x
        url = f'{baseurl}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
        browser.get(url)

        # assign carrier
        lcr_carrier_link = browser.find_element_by_id(f'{PREFIX}hlCarrierLCRLink')
        lcr_carrier_link.click()
    
        # volume carrier only check
        volume_only = len(browser.find_elements(By.ID, f'{PREFIX}LineVolumeDiv'))
    
        if volume_only:
            print(load_id + ' is volume only')
        else:
            # wait until the rate table populates and becomes clickable
            WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, f'{PREFIX}objRateEngine_gvRates_ctl02_lnkQuoteNow')))

            # carrier filter logic
            rows = browser.find_elements_by_css_selector('tr.select-tooltip')
            buttons = browser.find_elements_by_css_selector('a.button-link')

            button_index = ''

            for y in rows:
                row_index = rows.index(y)
                carrier_name = rows[row_index].get_attribute('title')
                
                # carrier filters; if enabling or disabling, modify IF block below
                roadrunner_check = carrier_name.lower().find('roadrunner') < 0
                clearlane_check = carrier_name.lower().find('clear lane') < 0
                frontline_check = carrier_name.lower().find('frontline') < 0
                tradeshow_check = carrier_name.lower().find('trade show') < 0
                overnite_check = carrier_name.lower().find('best overnite') < 0
                central_check = carrier_name.lower().find('central freight') < 0
                custom_check = carrier_name.lower().find('custom companies') < 0
                
                if tradeshow_check and frontline_check and clearlane_check and overnite_check and custom_check and roadrunner_check and central_check:
                    button_index = row_index * 2
                    break 

            buttons[button_index].click()
            WebDriverWait(browser, timeout=30).until(EC.element_to_be_clickable((By.ID, f'{PREFIX}divCarrierInfo')))
            carrier_info = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCarrierInfo']/div[1]/strong").text

            print(load_id)
            print(carrier_info)
            with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
                carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                carrier_writer.writerow([load_id, carrier_info])
    except Exception as e:
        print(load_id + ' threw ' + repr(e))
        with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
            carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            carrier_writer.writerow([load_id, repr(e)])

browser.quit()
          


# def carrier_filter(carrier_dict):
#         for key in carrier_dict:
#             carrier_dict[key] = carrier_name.lower().find(key) < 0