import os
import pandas as pd
import time
import tms_login as tms
from datetime import date

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

#compares list of files in Downloads folder after downloading file to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    print(file_name + ' downloaded.')
elif len(change) == 0:
    print('No file downloaded.')
else:
    print ('More than one file downloaded.')
    
# sets filepath to downloaded file and create DataFrame from file 
# output file extension is .xls but is actually.html format

filepath = DOWNLOAD_FOLDER + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]

# grabs list of load numbers and load count, dropping the Totals row
load_list_numbers = list(df['Load #'])[:-1]
load_list = [str(x) for x in load_list_numbers]
load_count = len(df.index) -1

print(load_list)
print(str(load_count) + ' loads entered today.')