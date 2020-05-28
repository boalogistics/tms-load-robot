import getpass, json, logging, logging.config, os, time
import pandas as pd, tms_login as tms
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

def costco_discount(city, pallets, retail):
    # subtract 1 from pallets argument for list index
    discount_rate = costco_discount_dict[city][pallets - 1]
    # round to nearest multiple of 5
    reduction_value = -5 * round(retail * discount_rate) / 5
    return reduction_value

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
report_code = '82D85081FF9F'
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

# look up table in json for Costco location x Pallets
costco_discount_dict = json.load(open('db/costco_table.json', 'r'))

for x in load_table.index:
    try:        
        load_id = str(load_table['Load #'][x])
   
        # how to deal with multistop
        consignee_name = load_table['Consignee'][x].upper()
        consignee_city = load_table['C/ City'][x]
        pallets = load_table['Pallets'][x]
        is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in costco_discount_dict and pallets < 11

        edit_pricing = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentCostPop.aspx?loadid='+load_id
        browser.get(edit_pricing)

        td_list = browser.find_elements_by_tag_name('td')
        discount_exists = any(td.text == 'Discount:' for td in td_list)
        
        while not discount_exists:
            supplemental_select = Select(browser.find_element_by_id('ddlAddSupplementals'))
            try:
                supplemental_select.select_by_value('55')
            except Exception as e:
                logging.exception(load_id + ' threw ' + repr(e))
            add_button = browser.find_element_by_id('btnAddSupplemental')
            add_button.click()
            td_list = browser.find_elements_by_tag_name('td')
            discount_exists = any(td.text == 'Discount:' for td in td_list)

        base_retail = load_table['Base Retail'][x]

        if is_costco:
            discount = str(costco_discount(consignee_city, pallets, base_retail))
        else:
            discount = str(base_retail * -0.0415)

        discount_box_pos = [td.text for td in td_list].index('Discount:')
        # input box in next TD cell after Discount label
        discount_cell = td_list[discount_box_pos + 1]
        discount_input = discount_cell.find_element_by_tag_name('input')
        discount_input.send_keys(Keys.CONTROL + 'a')
        discount_input.send_keys(Keys.DELETE)
        discount_input.send_keys(discount)

        save_button = browser.find_element_by_id('btnUpdateCosts')
        save_button.click()
        logging.info(load_id + ' base retail ' + str(base_retail) + ' discounted '  + discount + '('+ str(float(discount)/base_retail) + ')')
    except Exception as e:
        logging.info(load_id + ' threw ' + repr(e))

browser.quit()
print('Browser closed.')
# costco_discount_dict.close()

os.startfile('logs\\pricer.log')