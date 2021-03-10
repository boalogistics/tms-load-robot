import getpass
import logging
import logging.config
import os
import sys
import time
from datetime import date, datetime, timedelta
import pandas as pd
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tms_login as tms

today = date.today()

# set up start date and end date for filter
# if no args passed automatically use prev bus. day to today
if len(sys.argv) < 2:
    weekday = datetime.weekday(today)

    # checks if today is Monday to calculate previous business day 1pm
    if weekday == 0:
        subtract_day = 2
    else:
        subtract_day = 0

    s_date = today + timedelta(-1 - subtract_day)
    e_date = today
    datestamp = today
elif len(sys.argv) == 3:
    # takes args start and end dates as MMDD ex. 0420 = APR 20
    s_date = date(today.year, int(sys.argv[1][:2]), int(sys.argv[1][2:]))
    e_date = date(today.year, int(sys.argv[2][:2]), int(sys.argv[2][2:]))
    datestamp = e_date
else:
    print('Error: Need 2 arguments: start and end dates in MMDD format.')
    sys.exit()

start = s_date.strftime("%m/%d/%Y 13:00:01")
end = e_date.strftime("%m/%d/%Y 13:00:00")

# initialize logger
print('Initializing logger...')
logging.config.fileConfig(fname='logs/cfg/book.conf')
logger = logging.getLogger('')

# daily report isolating single day
log_filename = 'logs\\book' + datestamp.strftime('_%m%d%Y_') + '.csv'
report = logging.FileHandler(filename=log_filename)
formatter = logging.Formatter()
report.setFormatter(formatter)
logger.addHandler(report)
print('Logger initialized.')

# constant file for emailing
exportreport = logging.FileHandler(filename='logs/book_export.csv', mode='w+')
exportreport.setFormatter(formatter)
logger.addHandler(exportreport)

# check if on citrx ('nt') or pi
if os.name == 'nt':
    # set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
    DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads\\"
else:
    # constant for downloads folder - Pi default for Chromium
    DOWNLOAD_FOLDER = '/home/pi/Downloads/'

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)
print('Logged into TMS.')

# enter report code into report_code variable
# "Daily Booking Report" report
report_code = '3092F43103C3'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={report_code}'
browser.get(report_url)

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
print('Retrieved entry report.')

# list of files in Downloads folder after downloading to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(f'{file_name} downloaded.')
elif len(change) == 0:
    logging.info('No file downloaded.')
else:
    logging.info('More than one file downloaded.')

# sets filepath to downloaded file and create DataFrame from file
# output file extension is .xls but is actually.html format

filepath = f'{DOWNLOAD_FOLDER}{file_name}'
data = pd.read_html(filepath)
df = data[0]

# grabs list of load numbers and load count, dropping the Totals row
load_list_numbers = list(df['Load #'])[:-1]
load_list = [str(load_num) for load_num in load_list_numbers]
load_count = len(df.index) - 1

logging.info(load_list)
logging.info(f'{load_count} loads entered today.')


# variables to count final results of loads
loads_booked = 0
loads_not_booked = 0

browser = tms.login(url)

PREFIX = 'ctl00_BodyContent_'

for x in load_list:
    load_id = x
    load_url = f'{url}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
    browser.get(load_url)

    # verify client is in good standing without credit hold
    WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}ctlWarningsVertical_lblCreditWarnings')))
    client_credit = browser.find_element_by_id(f'{PREFIX}ctlWarningsVertical_lblCreditWarnings').text.upper()
    client_credit_exceeded = client_credit.find('EXCEEDED') != -1

    if client_credit_exceeded:
        client_name = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCustomerInfo']/div[1]/a").text
        logging.info(f'{load_id} not booked. Client {client_name} has exceeded credit limit.')
        loads_not_booked += 1
    else:
        # check if load is already in booked/dispatched/cancelled status and trace priority
        WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, 'lblTitle')))
        status = browser.find_element_by_id('lblTitle').text.upper()

        quote_status = status.find('QUOTED') > -1

        if quote_status:
            js_book = 'WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$BodyContent$lbBookShipment", "", true, "", "", false, true))'
            browser.execute_script(js_book)
            logging.info(f'Load {load_id} booked.')
            loads_booked += 1
        else:
            logging.info(f'{load_id} not booked. {status}')
            loads_not_booked += 1

        trace_priority = status.find('TRACE') > -1

        if not trace_priority:
            edit_shipment = f'{url}App_BW/staff/shipment/EditShipmentPop.aspx?loadid={load_id}'
            browser.get(edit_shipment)

            # variable and selections for Equipment Types
            WebDriverWait(browser, timeout=30).until(EC.presence_of_element_located((By.ID, f'{PREFIX}priority')))
            priority = Select(browser.find_element_by_id(f'{PREFIX}priority'))
            priority.select_by_value('6')

            # save changes
            update_btn = browser.find_element_by_css_selector('[value="Update"]')
            update_btn.click()

browser.quit()

logging.info(f'{loads_booked} loads booked.')
logging.info(f'{loads_not_booked} loads not booked.')
print('Browser closed.')

logging.shutdown()
print(f'Session log saved to {log_filename}.')
print('Logger closed.')

if os.name == 'nt':
    os.startfile(log_filename)
