# import selenium webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import Select

# activate chrome driver
browser = webdriver.Chrome()
browser.implicitly_wait(3)
browser.maximize_window()
browser.get("https://boa.3plsystemscloud.com/")

# page elements to login
boa_user = browser.find_element_by_id("txb-username")
boa_pw = browser.find_element_by_id("txb-password")
login_button = browser.find_element_by_id("ctl00_ContentBody_butLogin")

# login credentials
boa_user.send_keys("***EMAIL HERE***")
boa_pw.send_keys("***PASSWORD HERE***")
login_button.click()

# put FOR loop here to loop through list of load numbers
loadlist = ['147136'
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
    browser.implicitly_wait(10)

    # set handle to popup and switches to popup
    popup = browser.window_handles[1]
    browser.switch_to.window(popup)
    
    # variable and selections for Equipment Types
    priority = Select(browser.find_element_by_id("ctl00_BodyContent_priority"))
    priority.select_by_value("6")
    
    # save changes
    updButton = browser.find_element_by_css_selector('[value="Update"]')
    updButton.click()
    browser.implicitly_wait(3)
        
    browser.switch_to.window(og_window)
    
    # put exception handler to skip if load is already in booked/dispatched/cancelled status 
    
    status = browser.find_element_by_id("lblTitle").text.upper()
    quote_status = status.find('QUOTED') > -1   
    
    if quote_status:
        bookshipment = browser.find_element_by_id("ctl00_BodyContent_spnBookShipment")
        # dispatch = browser.find_element_by_id("ctl00_BodyContent_spnDispatchLink")
        # ratecon = browser.find_element_by_id("ctl00_BodyContent_spnDispatch")
        bookshipment.click()
        browser.implicitly_wait(5)
        # dispatch.click()
        # browser.implicitly_wait(5)
        # ratecon.click()
        # browser.implicitly_wait(5)

browser.quit()

# need to start grouping into functions and classes, then adding exception handlers and logging