import tms_login as tms
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# variables to count final results of loads
loads_dispatched = 0
loads_not_dispatched = 0

url = "https://boa.3plsystemscloud.com/"

browser = tms.login(url)


# put FOR loop here to loop through list of load numbers
loadlist = [['148323', '5709']
]

for x in loadlist:
    load_id = x[0]
    carrier_id = x[1]
    load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(load_url)
    
    # verify load is not already dispatched status    
    status = browser.find_element_by_id('lblTitle').text.upper()
    booked = status.find('BOOKED') != -1   
    
    if booked:
        # set first window handle
        og_window = browser.window_handles[0]

        # assign carrier
        vol_carrier_link = browser.find_element_by_id('ctl00_BodyContent_hlCarrierVolLink')
        vol_carrier_link.click()
        carrier_select = Select(browser.find_element_by_id('ctl00_BodyContent_ListBoxCarriers'))
        carrier_select.select_by_value(carrier_id)
        select_carrier_btn = browser.find_element_by_id('ctl00_BodyContent_SelectCarrierSave')
        select_carrier_btn.click()
        WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, 'ctl00_BodyContent_ctlWarningsVertical_lblInsuranceWarnings')))

        # verify carrier insurance on file is not expired
        carrier_insurance = browser.find_element_by_id('ctl00_BodyContent_ctlWarningsVertical_lblInsuranceWarnings').text.upper()
        carrier_insurance_expired = carrier_insurance.find('EXPIRED') != -1 

        if carrier_insurance_expired:
            print(load_id + ' not dispatched. Carrier insurance on file is expired.')
            loads_not_dispatched += 1
        else:
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

            print('Load number ' + load_id + ' dispatched!')
            loads_dispatched += 1
    else:
        print('Auto dispatcher script did not dispatch: ' + status)
        loads_not_dispatched += 1

browser.quit()

print(str(loads_dispatched) + ' loads dispatched.')
print(str(loads_not_dispatched) + ' loads not dispatched.')
print('Browser closed.')