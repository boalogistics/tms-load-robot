import getpass
import os
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
import tms_login as tms
from data_extract import open_sheet

sheet = open_sheet('Warehousing Sheet Data Feed', 'client_update_query')
loads = sheet.get_all_values() 

load_list = [load[0] for load in loads[1:]]
print(load_list)

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into REPORT_CODE constant
# "Manifest" report
REPORT_CODE = '5B05B05BE9D9'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={REPORT_CODE}'
browser.get(report_url)

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in load_list[:-1]:
    loadno.send_keys(f'\'{x}\',')
loadno.send_keys(f'\'{load_list[-1]}\'')

# save & view report, then download
save_report_btn = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_report_btn.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(1)
browser.quit()

# list of files in Downloads folder after downloading to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
elif len(change) == 0:
    pass
else:
    pass

# output file extension is .xls but is actually.html format
filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
data = pd.read_html(filepath)
df = data[0]
load_table = df.drop(len(df.index)-1).values.tolist()

#TODO rename sheet to proper name
manifest = open_sheet('MANIFEST CREATOR 1.0', 'tms_data')

flat_table = [item for sublist in load_table for item in sublist]
range_notation = 'A2:H' + str(len(load_table) + 1)

cell_list = manifest.range(range_notation)

for index, cell in enumerate(cell_list):
    cell.value = flat_table[index]

manifest.update_cells(cell_list)

print('Manifest updated!')
