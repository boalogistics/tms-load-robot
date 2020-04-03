import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

# activate chrome driver
browser = webdriver.Firefox()
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
loadlist = ['151756', 
'152313', 
'151721', 
'151650', 
'151633', 
'151637', 
'152100', 
'151952', 
'151782', 
'151764', 
'152098', 
'152309', 
'152320', 
'151879', 
'151697', 
'152166', 
'151941', 
'151748', 
'151895', 
'152008', 
'152125', 
'151919', 
'151685', 
'152148', 
'152220', 
'152149', 
'152209', 
'151635', 
'152195', 
'151631', 
'151686', 
'151868', 
'152256', 
'152259', 
'151920', 
'151883', 
'152241', 
'152182', 
'151657', 
'152277', 
'152009', 
'152284', 
'152154', 
'151958', 
'152157', 
'151915', 
'152045', 
'152144', 
'151651', 
'151639', 
'152018', 
'152020', 
'151931', 
'152310', 
'151880', 
'151776', 
'152161', 
'151694', 
'152240', 
'152047', 
'152086', 
'152022', 
'152181', 
'151946', 
'151759', 
'152324', 
'151951', 
'152132', 
'151911', 
'152038', 
'152289', 
'152074', 
'151664', 
'152276', 
'151835', 
'151932', 
'151871', 
'151968', 
'152186', 
'151954', 
'151898', 
'152301', 
'152302', 
'152112', 
'151682', 
'152247', 
'151726', 
'152253', 
'152117', 
'151758', 
'152192', 
'152034', 
'152264', 
'151897', 
'151740', 
'151648', 
'152146', 
'151763', 
'152317', 
'151922', 
'151976', 
'151948', 
'151810', 
'152314', 
'152115', 
'151751', 
'151844', 
'151771', 
'152163', 
'151982', 
'151817', 
'152138', 
'151729', 
'152012', 
'152004', 
'152212', 
'151907', 
'151801', 
'152215', 
'151921', 
'152139', 
'152222', 
'152191', 
'152267', 
'152303', 
'152088', 
'152156', 
'152068', 
'152013', 
'151805', 
'151830', 
'152090', 
'152248', 
'152159', 
'151789', 
'151742', 
'151998', 
'151877', 
'152232', 
'152104', 
'151823', 
'152023', 
'152150', 
'152142', 
'152281', 
'151987', 
'152048', 
'151824', 
'151757', 
'151872', 
'152153', 
'151878', 
'152177', 
'152300', 
'152076', 
'151698', 
'151997', 
'151816', 
'151772', 
'152316', 
'151834', 
'151849', 
'152254', 
'151961', 
'152183', 
'152035', 
'151744', 
'151909', 
'152295', 
'151832', 
'152079', 
'151916', 
'151953', 
'151728', 
'151797', 
'151799', 
'151727', 
'152160', 
'151818', 
'151730', 
'151862', 
'152053', 
'151738', 
'151914', 
'151646', 
'152217', 
'151957', 
'151991', 
'151804', 
'151765', 
'152044', 
'152087', 
'151691', 
'151939', 
'151693', 
'151821', 
'151977', 
'152033', 
'152051', 
'151670', 
'152031', 
'151719', 
'151716', 
'151901', 
'152280', 
'151645', 
'151947', 
'152140', 
'151986', 
'152266', 
'152229', 
'152327', 
'152096', 
'151666', 
'152082', 
'151720', 
'151881', 
'152268', 
'152094', 
'151891', 
'152007', 
'151749', 
'151787', 
'151662', 
'151902', 
'151750', 
'152065', 
'152085', 
'152297', 
'152292', 
'152111', 
'151767', 
'152054', 
'152227', 
'152164', 
'151654', 
'152169', 
'151669', 
'151663', 
'152179', 
'151890', 
'152167', 
'152170', 
'152315', 
'152238', 
'151701', 
'151990', 
'151899', 
'152176', 
'151741', 
'152127', 
'151859', 
'151923', 
'151861', 
'152185', 
'151702', 
'152028', 
'151796', 
'151786', 
'152069', 
'152223', 
'151778', 
'151700', 
'152078', 
'151737', 
'151985', 
'151704', 
'152092', 
'152145', 
'152040', 
'151747', 
'151745', 
'151926', 
'152126', 
'151668', 
'152279', 
'151807', 
'151690', 
'152187', 
'151867', 
'151828', 
'151900', 
'152258', 
'151734', 
'152294', 
'152211', 
'151912', 
'152039', 
'151766', 
'152263', 
'152014', 
'152063', 
'151903', 
'152172', 
'152225'
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
    print(volume_only)
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
        print(button_index)
        print(load_id)
        print(carrier_info)
        with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
            carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            carrier_writer.writerow([load_id, carrier_info])
