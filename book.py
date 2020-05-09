import logging, logging.config
import tms_login as tms
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# initialize logger
logging.config.fileConfig(fname='logger.conf')
logger = logging.getLogger('')

# variables to count final results of loads
loads_booked = 0
loads_not_booked = 0

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)


load_list = ['158904', '158906', '158907', '158908', '158909', '158910', '158922', '158926', '158930', '158923', '158927', '158931', '158921', '158925', '158929', '158920', '158924', '158928', '158932', '158936', '158940', '158933', '158937', '158935', '158939', '158934', '158938', '158942', '158946', '158943', '158947', '158941', '158945', '158944', '158948', '158968', '158972', '158976', '158980', '158969', '158973', '158977', '158981', '158971', '158975', '158979', '158970', '158974', '158978', '158982', '158986', '158990', '158983', '158987', '158991', '158985', '158989', '158984', '158988', '158992', '158996', '159000', '159004', '158993', '158997', '159001', '159005', '158995', '158999', '159003', '159007', '158994', '158998', '159002', '159006', '159012', '159013']

for x in load_list:
    load_id = x
    load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(load_url)

    # verify client is in good standing without credit hold
    client_credit =  browser.find_element_by_id('ctl00_BodyContent_ctlWarningsVertical_lblCreditWarnings').text.upper()
    client_credit_exceeded = client_credit.find('EXCEEDED') != -1

    if client_credit_exceeded:
        client_name = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divCustomerInfo']/div[1]/a").text
        logging.info(load_id + ' not booked. Client {} has exceeded credit limit.'.format(client_name))
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
            logging.info(load_id + ' booked.')
            loads_booked += 1
        else:
            logging.info(load_id + ' not booked. ' + status)
            loads_not_booked += 1

browser.quit()

logging.info(str(loads_booked) + ' loads booked.')
logging.info(str(loads_not_booked) + ' loads not booked.')
print('Browser closed.')