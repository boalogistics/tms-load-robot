import tms_login as tms
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options

# variables to count final results of loads
loads_booked = 0
loads_not_booked = 0

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)


loadlist = ['150095', '150094', '150093', '150096', '150100', '150104', '150108', '150112', '150116', '150097', '150101', '150105', '150109', '150113', '150117', '150098', '150102', '150106', '150110', '150114', '150118', '150099', '150103', '150107', '150111', '150115', '150119', '150123', '150122', '150126', '150121', '150125', '150120', '150124', '150132', '150136', '150133', '150137', '150134', '150138', '150135', '150139', '150143', '150142', '150141', '150145', '150140', '150144', '150149', '150154', '150155', '150157', '150158', '150160', '150161', '150164', '150176', '150177', '150175', '150174', '150150'
]

for x in loadlist:
    load_id = x
    url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(url)

    # verify client is is good standing without credit hold
    client_credit =  browser.find_element_by_id('ctl00_BodyContent_ctlWarningsVertical_lblCreditWarnings').text.upper()
    client_credit_exceeded = client_credit.find('EXCEEDED') != -1

    if client_credit_exceeded:
        print(load_id + ' not booked. Credit limit on account is exceeded.')
        loads_not_booked += 1
    else:
        # check if load is already in booked/dispatched/cancelled status and trace priority
        status = browser.find_element_by_id('lblTitle').text.upper()
        
        not_trace_priority = status.find('TRACE') == -1  
        
        if not_trace_priority:
            # set first window handle
            og_window = browser.window_handles[0]
            
            # open "Edit Shipment" window
            editShipment = browser.find_element_by_link_text('Edit Shipment')
            editShipment.click()
            WebDriverWait(browser, timeout=30).until(EC.number_of_windows_to_be(2))

            # set handle to popup and switches to popup
            popup = browser.window_handles[1]
            browser.switch_to.window(popup)
            
            # variable and selections for Equipment Types
            priority = Select(browser.find_element_by_id('ctl00_BodyContent_priority'))
            priority.select_by_value('6')
            
            # save changes
            updButton = browser.find_element_by_css_selector('[value="Update"]')
            updButton.click()
                
            browser.switch_to.window(og_window)
        
        quote_status = status.find('QUOTED') > -1   
        
        if quote_status:
            bookshipment = browser.find_element_by_id('ctl00_BodyContent_spnBookShipment')
            bookshipment.click()
            print(load_id + ' booked.')
            loads_booked += 1
        else:
            print(load_id + ' not booked. ' + status)
            loads_not_booked += 1

browser.quit()

print(str(loads_booked) + ' loads booked.')
print(str(loads_not_booked) + ' loads not booked.')
print('Browser closed.')