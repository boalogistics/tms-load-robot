## TODO add code to handle alert on LCR and Edit profile window

import csv
import tms_login as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# put FOR loop here to loop through list of load numbers
loadlist = ['157658',
'157659',
'157660',
'157661',
'157662',
'157663',
'157664',
'157665',
'157666',
'157667',
'157668',
'157669',
'157670',
'157671',
'157672',
'157673',
'157674',
'157675',
'157676',
'157677',
'157678',
'157679',
'157680',
'157681',
'157682',
'157683',
'157684',
'157685',
'157686',
'157687',
'157688',
'157689',
'157690',
'157691',
'157692',
'157693',
'157694',
'157695',
'157696',
'157697',
'157698',
'157699',
'157700',
'157701',
'157702',
'157703',
'157704',
'157705',
'157706',
'157707',
'157708',
'157709',
'157710',
'157711',
'157712',
'157713',
'157714',
'157715',
'157716',
'157717',
'157718',
'157719',
'157720',
'157721',
'157722',
'157723',
'157724',
'157725',
'157726',
'157727',
'157728',
'157729',
'157730',
'157731',
'157732',
'157733',
'157734',
'157735',
'157736',
'157737',
'157738',
'157739',
'157740',
'157741',
'157742',
'157743',
'157744',
'157745',
'157746',
'157747',
'157748',
'157749',
'157750',
'157751',
'157752',
'157753',
'157754',
'157755',
'157756',
'157757',
'157758',
'157759',
'157760',
'157761',
'157762',
'157763',
'157764',
'157765',
'157766',
'157767',
'157768',
'157769',
'157770',
'157771',
'157772',
'157773',
'157774',
'157775',
'157776',
'157777',
'157778',
'157779',
'157780',
'157781',
'157782',
'157783',
'157784',
'157785',
'157786'
]

for x in loadlist:
    try:
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
            WebDriverWait(browser, timeout=30).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_divCarrierInfo')))
            carrier_info = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divCarrierInfo']/div[1]/strong").text

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
          


# def carrier_filter(carrier_dict):
#         for key in carrier_dict:
#             carrier_dict[key] = carrier_name.lower().find(key) < 0