# import selenium webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
loadlist = [['145448', '1234']
]

for x in loadlist:
    load_id = x[0]
    carrier_id = x[1]
    url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(url)
    
    # verify load is not already dispatched status    
    status = browser.find_element_by_id('lblTitle').text.upper()
    not_dispatched = status.find('DISPATCHED') == -1   
    
    if not_dispatched:
        # set first window handle
        og_window = browser.window_handles[0]

        # assign carrier
        vol_carrier_link = browser.find_element_by_id('ctl00_BodyContent_hlCarrierVolLink')
        vol_carrier_link.click()
        carrier_select = Select(browser.find_element_by_id('ctl00_BodyContent_ListBoxCarriers'))
        carrier_select.select_by_value(carrier_id)
        select_carrier_btn = browser.find_element_by_id('ctl00_BodyContent_SelectCarrierSave')
        select_carrier_btn.click()

        # dispatch
        dispatch_link = browser.find_element_by_id('ctl00_BodyContent_lbDispatchLink')
        dispatch_link.click()
        WebDriverWait(browser, timeout=30).until(EC.number_of_windows_to_be(2))

        # set handle to popup and switches to popup
        popup = browser.window_handles[1]
        browser.switch_to.window(popup)

        # variable and selections for Priority
        dispatch_btn = browser.find_element_by_id('btnDispatchComplete')
        dispatch_btn.click()       
        browser.switch_to.window(og_window)