## TODO add error catcher for timing out and/or alert on LCR page to skip current load number

import csv
import tms_login as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# put FOR loop here to loop through list of load numbers
loadlist = [
'157310',
'157311',
'157312',
'157313',
'157314',
'157315',
'157316',
'157317',
'157318',
'157319',
'157320',
'157321',
'157322',
'157323',
'157324',
'157325',
'157326',
'157327',
'157328',
'157329',
'157330',
'157331',
'157332',
'157333',
'157334',
'157335',
'157336',
'157337',
'157338',
'157339',
'157340',
'157341',
'157342',
'157343',
'157344',
'157345',
'157346',
'157347',
'157348',
'157349',
'157350',
'157351',
'157352',
'157353',
'157354',
'157355',
'157356',
'157357',
'157358',
'157359',
'157360',
'157361',
'157362',
'157363',
'157364',
'157365',
'157366',
'157367',
'157368',
'157369',
'157370',
'157371',
'157372',
'157373',
'157374',
'157375',
'157376',
'157377',
'157378',
'157379',
'157380',
'157381',
'157382',
'157383',
'157384',
'157385',
'157386',
'157387',
'157388',
'157389',
'157390',
'157391',
'157392',
'157393',
'157394',
'157395',
'157396',
'157397',
'157398',
'157399',
'157400',
'157401',
'157402',
'157403',
'157404',
'157405',
'157406',
'157407',
'157408',
'157409',
'157410',
'157411',
'157412',
'157413',
'157414',
'157415',
'157416',
'157417',
'157418',
'157419',
'157420',
'157421',
'157422',
'157423',
'157424',
'157425',
'157426',
'157427',
'157428',
'157429',
'157430',
'157431',
'157432',
'157433',
'157434',
'157435',
'157436',
'157437',
'157438',
'157439',
'157440',
'157441',
'157442',
'157443',
'157444',
'157445',
'157446',
'157447',
'157448',
'157449',
'157450',
'157451',
'157452',
'157453',
'157454',
'157455',
'157456',
'157457',
'157458',
'157459',
'157460',
'157461',
'157462',
'157463',
'157464',
'157465',
'157466',
'157467',
'157468',
'157469',
'157470',
'157471',
'157472',
'157473',
'157474',
'157475',
'157476',
'157477',
'157478',
'157479',
'157480',
'157481',
'157482',
'157483',
'157484',
'157485',
'157486',
'157487',
'157488',
'157489',
'157490',
'157491',
'157492',
'157493',
'157494',
'157495',
'157496',
'157497',
'157498',
'157499',
'157500',
'157501',
'157502',
'157503',
'157504',
'157505',
'157506',
'157507',
'157508',
'157509',
'157510',
'157511',
'157512',
'157513',
'157514',
'157515',
'157516',
'157517',
'157518',
'157519',
'157520',
'157521',
'157522',
'157523',
'157524',
'157525',
'157526',
'157527',
'157528',
'157529',
'157530',
'157531',
'157532',
'157533',
'157534',
'157535',
'157536',
'157537',
'157538',
'157539',
'157540',
'157541',
'157542',
'157543',
'157544',
'157545',
'157546',
'157547',
'157548',
'157549',
'157550',
'157551'

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
            with open('lcr-carrier-list-copy.csv', mode='a+') as carrier_list:
                carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                carrier_writer.writerow([load_id, carrier_info])
    except Exception as e:
        print(load_id + ' threw ' + repr(e))
        with open('lcr-carrier-list-copy.csv', mode='a+') as carrier_list:
            carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            carrier_writer.writerow([load_id, repr(e)])

# def carrier_filter(carrier_dict):
#         for key in carrier_dict:
#             carrier_dict[key] = carrier_name.lower().find(key) < 0