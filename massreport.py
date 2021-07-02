import sys
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tms_login as tms


# set up start date and end date for filter
# exit if no args
if len(sys.argv) != 3:
    print('Error: Need 2 arguments: start and end dates in MMDDYY format.')
    sys.exit()

# takes args start and end dates as MMDDYY ex. 042020 = APR 20 2020
s_date = date(int('20' + sys.argv[1][4:]), int(sys.argv[1][:2]), int(sys.argv[1][2:4]))
f_date = date(int('20' + sys.argv[2][4:]), int(sys.argv[2][:2]), int(sys.argv[2][2:4]))


url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)
print('Logged into TMS.')

# enter report code into report_code variable
# "OTD Analysis" report
report_code = '1E31D51E3121'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={report_code}'
browser.get(report_url)

# add 1 month to start date for end date (accounts for 28/30/31 day months)
e_date = s_date + relativedelta(months=1)

# repeat until reach final date
while e_date < f_date or s_date < f_date:

    start = s_date.strftime("%m/%d/%Y 00:00:00")
    end = e_date.strftime("%m/%d/%Y 23:59:59")

    print(start)
    print(end)

    startbox = browser.find_element_by_xpath("//td[6]/input[@class='filter between'][1]")
    endbox = browser.find_element_by_xpath("//td[6]/input[@class='filter between'][2]")
    startbox.clear()
    startbox.send_keys(start)
    endbox.clear()
    endbox.send_keys(end)

    # # save & view report, then download
    save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
    save_button.click()
    browser.implicitly_wait(3)
    download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
    download.click()
    time.sleep(3)
    print('Downloaded.')

    # next iteration
    s_date = e_date
    e_date = s_date + relativedelta(months=1)

browser.close()