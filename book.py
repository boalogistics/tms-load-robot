import tms_login as tms
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

url = "https://boa.3plsystemscloud.com/"

browser = tms.login(url)

# put FOR loop here to loop through list of load numbers
loadlist = [
    '149114', 

]

for x in loadlist:
    load_id = x
    url = "https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid="+load_id
    browser.get(url)
    
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
    
    # check if load is already in booked/dispatched/cancelled status 
    status = browser.find_element_by_id("lblTitle").text.upper()
    quote_status = status.find('QUOTED') > -1   
    
    if quote_status:
        bookshipment = browser.find_element_by_id("ctl00_BodyContent_spnBookShipment")
        bookshipment.click()
        print(load_id + ' booked.')
    else:
        print(load_id + ' not booked. ' + status)

browser.quit()