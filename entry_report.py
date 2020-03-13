from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import os
import pandas as pd
import time

# list of files before downloading
before = os.listdir(r"C:\Users\BOA\Downloads")

# activate chrome driver
browser = webdriver.Chrome()
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

# enter report code into report_code variable
# "Daily Booking Report" report
report_code = "3092F43103C3"
url = "https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code="+report_code
browser.get(url)

# sets up start date and end date for filter
# checks today's date to calculate next 2 business days

today = date.today()

s_date = today
str_s_date = s_date.strftime("%m/%d/%Y")

start = str_s_date + " 00:00:00"
end = str_s_date + " 23:59:59"

# set up variables for parameter fields
startbox = browser.find_element_by_xpath("//td[1]/input[@class='filter between'][1]")
endbox = browser.find_element_by_xpath("//td[1]/input[@class='filter between'][2]")

# inserts new parameters
startbox.clear()
startbox.send_keys(start)
endbox.clear()
endbox.send_keys(end)

# save & view report, then download
save_button = browser.find_element_by_id("ctl00_ContentBody_butSaveView")
save_button.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id("ctl00_ContentBody_butExportToExcel")
download.click()
time.sleep(3)

browser.close()

#compares list of files in Downloads folder after downloading file to extract filename
after = os.listdir(r"C:\Users\BOA\Downloads")
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    print(file_name + " downloaded.")
else:
    print ("More than one file or no file downloaded")
    
# sets filepath to downloaded file and create DataFrame from file 
# *output file extension is .xls but is actually.html format

filepath = r"C:\Users\BOA\Downloads" + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]

# grabs list of load numbers and load count, dropping the Totals row
load_list_numbers = list(df['Load #'])[:-1]
load_list = [str(x) for x in load_list_numbers]
load_count = len(df.index) -1

print(load_list)
print(str(load_count) + ' loads entered today.')