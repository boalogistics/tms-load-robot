import getpass, logging, logging.config, os, time
import pandas as pd, tms_login as tms
from discount import applydiscount

# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

# set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = "C:\\Users\\" + getpass.getuser().title() + "\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into report_code variable
# "Daily Booking Report" report
report_code = '23725A2291F1'
report_url = 'https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code=' + report_code
browser.get(report_url)

loadlist = ['157891', '157942', '157939', '156565', '156347', '157992', '157959']

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in loadlist[:-1]:
    loadno.send_keys('\'' + x + '\',')
loadno.send_keys('\'' + loadlist[-1] + '\'')

# save & view report, then download
save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_button.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(1)

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
    
# output file extension is .xls but is actually.html format
filepath = DOWNLOAD_FOLDER + "\\" + file_name
data = pd.read_html(filepath)
df = data[0]
load_table = df[['Load #', 'Consignee', 'C/ City', 'Pallets', 'Base Retail']].drop(len(df.index)-1)

applydiscount(load_table)

browser.quit()
print('Browser closed.')
# costco_discount_dict.close()

os.startfile('logs\\pricer.log')