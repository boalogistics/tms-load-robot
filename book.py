import tms_login as tms
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# variables to count final results of loads
loads_booked = 0
loads_not_booked = 0

url = "https://boa.3plsystemscloud.com/"

browser = tms.login(url)

# put FOR loop here to loop through list of load numbers
loadlist = [
    '149179', 
'149180', 
'149181', 
'149182', 
'149183', 
'149184', 
'149185', 
'149186', 
'149187', 
'149188', 
'149189', 
'149190', 
'149191', 
'149192', 
'149193', 
'149195', 
'149196', 
'149197', 
'149198', 
'149199', 
'149200', 
'149201', 
'149202', 
'149203', 
'149204', 
'149205', 
'149206', 
'149207', 
'149211', 
'149212', 
'149213', 
'149214', 
'149215', 
'149216', 
'149217', 
'149218', 
'149219', 
'149220', 
'149221', 
'149222', 
'149223', 
'149224', 
'149225', 
'149226', 
'149227', 
'149228', 
'149229', 
'149230', 
'149231', 
'149232', 
'149233', 
'149234', 
'149235', 
'149236', 
'149237', 
'149238', 
'149239', 
'149240', 
'149241', 
'149242', 
'149243', 
'149244', 
'149251', 
'149252', 
'149253', 
'149254', 
'149255', 
'149256', 
'149257', 
'149258', 
'149259', 
'149260', 
'149261', 
'149262', 
'149263', 
'149264', 
'149265', 
'149266', 
'149267', 
'149268', 
'149277', 
'149278', 
'149281', 
'149279', 
'149276', 
'149273', 
'149272', 
'148964', 
'148984', 
'149297', 
'149298', 
'149299', 
'149300', 
'149301', 
'149302', 
'149303', 
'149304', 
'149305', 
'149306', 
'149307', 
'149308', 
'149309', 
'149310', 
'149311', 
'149312', 
'149313', 
'149314', 
'149315', 
'149316', 
'149317', 
'149318', 
'149319', 
'149320', 
'149321', 
'149322', 
'149323', 
'149324', 
'149325', 
'149326', 
'149327', 
'149328', 
'149331', 
'149332', 
'149333', 
'149335', 
'149336', 
'148984', 
'148953', 
'149146', 
'149127', 
'149128', 
'149339' 
]

for x in loadlist:
    load_id = x
    url = "https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid="+load_id
    browser.get(url)

    # check if load is already in booked/dispatched/cancelled status and trace priority
    status = browser.find_element_by_id("lblTitle").text.upper()
    
    not_trace_priority = status.find('TRACE') == -1  
    
    if not_trace_priority:
        # set first window handle
        og_window = browser.window_handles[0]
        
        # open "Edit Shipment" window
        editShipment = browser.find_element_by_link_text("Edit Shipment")
        editShipment.click()
        WebDriverWait(browser, timeout=30).until(EC.number_of_windows_to_be(2))

        # set handle to popup and switches to popup
        popup = browser.window_handles[1]
        browser.switch_to.window(popup)
        
        # variable and selections for Equipment Types
        priority = Select(browser.find_element_by_id("ctl00_BodyContent_priority"))
        priority.select_by_value("6")
        
        # save changes
        updButton = browser.find_element_by_css_selector('[value="Update"]')
        updButton.click()
            
        browser.switch_to.window(og_window)
    
    quote_status = status.find('QUOTED') > -1   
    
    if quote_status:
        bookshipment = browser.find_element_by_id("ctl00_BodyContent_spnBookShipment")
        bookshipment.click()
        print(load_id + ' booked.')
        loads_booked += 1
    else:
        print(load_id + ' not booked. ' + status)
        loads_not_booked += 1

browser.quit()

print(str(loads_booked) + ' loads booked.')
print(str(loads_not_booked) + ' loads not booked.')