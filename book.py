# import selenium webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# activate headless mode
options = Options()
options.headless = True

# activate chrome driver
browser = webdriver.Chrome(options=options)
browser.implicitly_wait(3)
browser.maximize_window()
browser.get("https://boa.3plsystemscloud.com/")

# page elements to login
boa_user = browser.find_element_by_id("txb-username")
boa_pw = browser.find_element_by_id("txb-password")
login_button = browser.find_element_by_id("ctl00_ContentBody_butLogin")

# login credentials
boa_user.send_keys("daigo@boalogistics.com")
boa_pw.send_keys("ship12345")
login_button.click()

# put FOR loop here to loop through list of load numbers
loadlist = [
    '148916', 
    '148941', 
    '148942', 
    '148944', 
    '148947', 
    '148949', 
    '148952', 
    '148466', 
    '148771', 
    '148774', 
    '148779', 
    '148781', 
    '148791', 
    '148796', 
    '148798', 
    '148821', 
    '148852', 
    '148857', 
    '148859', 
    '148864', 
    '148871', 
    '148883', 
    '148904', 
    '148715', 
    '148935', 
    '148936', 
    '148937', 
    '148938', 
    '148939', 
    '148940', 
    '148943', 
    '148945', 
    '148946', 
    '148948', 
    '148950', 
    '148951', 
    '148953', 
    '148772', 
    '148822', 
    '148823', 
    '148825', 
    '148880', 
    '148902', 
    '148954', 
    '148851', 
    '148974', 
    '148975', 
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

browser.quit()