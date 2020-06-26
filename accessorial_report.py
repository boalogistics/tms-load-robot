import os, time
import pandas as pd
import tms_login as tms
from datetime import date

# set to Chrome default download folder
DOWNLOAD_FOLDER = "C:\\Users\\daigo\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# loop over Accessorial reports 1-8
reports = {
    'A1': '38738038E4E4',
    'A2': '38738039C4E4',
    'A3': '3873803A34E4',
    'A4': '3873803AA4E4',
    'A5': '3873803B14E4',
    'A6': '3873873724E4',
    'A7': '3873873794E4',
    'A8': '3873873804E4'
}

# List of load numbers to get accessorials for
load_nos = []
output = "'" + "', '".join(load_nos) + "'"

for key in reports:
    # list of files before downloading
    before = os.listdir(DOWNLOAD_FOLDER)
    
    report_code = reports[key]
    report_url = 'https://boa.3plsystemscloud.com/App_BW/staff/Reports/ReportViewer.aspx?code=' + report_code
    browser.get(report_url)

    browser.execute_script("document.getElementById('table-wherevalue').firstElementChild.firstElementChild.value =`" + output + "`;")

    # load_no_box = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
    # load_no_box.clear()
    # load_no_box.send_keys(output)
    

    # save & view report, then download
    save_button = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
    save_button.click()
    browser.implicitly_wait(30)
    download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
    download.click()
    time.sleep(3)

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
    df.drop(len(df.index) - 1, inplace=True)
    load_range = load_nos[0] + load_nos[-1] 

    filesave = DOWNLOAD_FOLDER + "\\access\\" + key + "_" + load_range + ".csv"

    df.to_csv(filesave, index = False)
    print("Saved file " + filesave + "!")
    
    new_source = DOWNLOAD_FOLDER + "\\access\\" + key + "-" + load_range + ".html"
    os.rename(filepath, new_source)
    print("Renamed " + filepath + " to " + new_source + "!")

browser.close()