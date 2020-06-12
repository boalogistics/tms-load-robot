import getpass, logging, logging.config, os, time
import pandas as pd, tms_login as tms
from datetime import date
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

today = date.today()
datestr = today
filename = 'logs/book' + datestr.strftime('_%m%d%Y_') + '.csv'

# initialize logger
logging.config.fileConfig(fname='logs/cfg/book.conf')
logger = logging.getLogger('')

# daily report isolating single day
report = logging.FileHandler(filename=filename)
formatter = logging.Formatter()
report.setFormatter(formatter)
logger.addHandler(report)

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = "C:\\Users\\" + getpass.getuser().title() + "\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into report_code variable
# "Daily Booking Report" report
report_code = '3092F43103C3'
report_url = 'https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code=' + report_code
browser.get(report_url)

s_date = today

start = s_date.strftime('%m/%d/%Y 00:00:00')
end = s_date.strftime('%m/%d/%Y 23:59:59')

startbox = browser.find_element_by_xpath("//td[1]/input[@class='filter between'][1]")
endbox = browser.find_element_by_xpath("//td[1]/input[@class='filter between'][2]")
startbox.clear()
startbox.send_keys(start)
endbox.clear()
endbox.send_keys(end)

# save & view report, then download
save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_button.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(3)

browser.close()

#compares list of files in Downloads folder after downloading file to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(file_name + ' downloaded.')
elif len(change) == 0:
    logging.info('No file downloaded.')
else:
    logging.info ('More than one file downloaded.')
    
# sets filepath to downloaded file and create DataFrame from file 
# output file extension is .xls but is actually.html format

filepath = DOWNLOAD_FOLDER + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]

# grabs list of load numbers and load count, dropping the Totals row
load_list_numbers = list(df['Load #'])[:-1]
load_list = [str(x) for x in load_list_numbers]
load_count = len(df.index) -1

logging.info(load_list)
logging.info(str(load_count) + ' loads entered today.')


# variables to count final results of loads
loads_booked = 0
loads_not_booked = 0

browser = tms.login(url)

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
        
        trace_priority = status.find('TRACE') > -1  
        
        if not trace_priority:
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

os.startfile(filename)