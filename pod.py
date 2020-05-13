import csv
import tms_login as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

f = open('pod_list.csv', 'a')

# put FOR loop here to loop through list of load numbers
loadlist = []

for x in loadlist:
    load_id = x
    url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
    browser.get(url)

    try:
        WebDriverWait(browser, timeout=1).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_divStoredDocs')))

        doc_table = browser.find_element_by_id('ctl00_BodyContent_divStoredDocs')
        doc_links = doc_table.find_elements_by_tag_name('a')
        
        if any(link.text == 'POD' for link in doc_links):
            print(load_id + ' has POD uploaded.')
            f.write(load_id + ' has POD uploaded.\n')
        else:
            print(load_id + ' has no POD uploaded.')
            f.write(load_id + ' has no POD uploaded.\n')
    except Exception as e:
        print(load_id + ' has no documents uploaded.')
        f.write(load_id + ' has no documents uploaded.\n')
        f.write(load_id + ' threw ' + repr(e) + '\n')
          
browser.quit()
print('Browser closed.')
f.close()
