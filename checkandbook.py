import os, time
import pandas as pd
import tms_login as tms
from datetime import date
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# set to Chrome default download folder
DOWNLOAD_FOLDER = "C:\\Users\\daigo\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into report_code variable
# "Daily Booking Report" report
report_code = '3092F43103C3'
report_url = 'https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code=' + report_code
browser.get(report_url)

today = date.today()
s_date = today
str_s_date = s_date.strftime('%m/%d/%Y')
# use below instead to specify a particular day other than today
#str_s_date = s_date.strftime("03/27/2020")

start = str_s_date + ' 00:00:00'
end = str_s_date + ' 23:59:59'
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

datestamp = s_date.strftime('%y%m%d')
log_file = open(datestamp + '_book.log', 'w')

def printlog(statement, logfile):
    print(statement)
    log_file.write(statement + '\n')

#compares list of files in Downloads folder after downloading file to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    printlog(file_name + ' downloaded.')
elif len(change) == 0:
    printlog('No file downloaded.', log_file)
else:
    printlog ('More than one file downloaded.', log_file)
    
# sets filepath to downloaded file and create DataFrame from file 
# output file extension is .xls but is actually.html format

filepath = DOWNLOAD_FOLDER + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]

# grabs list of load numbers and load count, dropping the Totals row
load_list_numbers = list(df['Load #'])[:-1]
load_list = [str(x) for x in load_list_numbers]
load_count = len(df.index) -1

printlog(load_list, log_file)
printlog(str(load_count) + ' loads entered today.', log_file)


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
        printlog(load_id + ' not booked. Client {} has exceeded credit limit.'.format(client_name), log_file)
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
            printlog(load_id + ' booked.', log_file)
            loads_booked += 1
        else:
            printlog(load_id + ' not booked. ' + status, log_file)
            loads_not_booked += 1

browser.quit()

printlog(str(loads_booked) + ' loads booked.', log_file)
printlog(str(loads_not_booked) + ' loads not booked.', log_file)
printlog('Browser closed.', log_file)
log_file.close()