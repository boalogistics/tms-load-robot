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


load_list = ['154356', '154501']

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

        quote_status = status.find('QUOTED') > -1   
        
        if quote_status:
            js_book = 'WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$BodyContent$lbBookShipment", "", true, "", "", false, true))'
            browser.execute_script(js_book)
            logging.info(load_id + ' booked.')
            loads_booked += 1
        else:
            logging.info(load_id + ' not booked. ' + status)
            loads_not_booked += 1
        
        not_trace_priority = status.find('TRACE') == -1  
        
        if not_trace_priority:
            edit_shipment = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/EditShipmentPop.aspx?loadid='+load_id
            browser.get(edit_shipment)

            # variable and selections for Equipment Types
            priority = Select(browser.find_element_by_id('ctl00_BodyContent_priority'))
            priority.select_by_value('6')
            
            # save changes
            update_btn = browser.find_element_by_css_selector('[value="Update"]')
            update_btn.click()

browser.quit()

logging.info(str(loads_booked) + ' loads booked.')
logging.info(str(loads_not_booked) + ' loads not booked.')
print('Browser closed.')