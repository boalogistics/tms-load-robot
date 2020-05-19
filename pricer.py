import json, logging, logging.config
import tms_login as tms
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

def costco_discount(city, pallets, retail):
    # look up table in json for Costco location x Pallets
    with open('costco_table.json', 'r') as f:
        costco_discount_dict = json.load(f)
    # subtract 1 from pallets argument for list index
    discount_rate = costco_discount_dict[city][pallets - 1]
    # round to nearest multiple of 5
    reduction_value = 5 * round(retail * discount_rate) / 5
    return reduction_value

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

loadlist = ['157887',
'156154',
'156161',
'157824',
'158933',
'156325'
]

for x in loadlist:
    try:        
        load_id = x
        load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
        browser.get(load_url)

        # how to deal with multistop
        consignee_name = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divShipRecLocations']/span/span[2]/div[@class='DivPanelB']/div[@class='PanelBodyForm']/table/tbody/tr[1]/td").text.upper()
        consignee_city = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divShipRecLocations']/span/span[2]/div[@class='DivPanelB']/div[@class='PanelBodyForm']/table/tbody/tr[3]/td").text
        is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in discount_dict
        pallets = 'getpalletcount'

        # add pallet counter here
        # how to account for non discount costco locations?
        # run a report for costco?

        edit_pricing = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentCostPop.aspx?loadid='+load_id
        browser.get(edit_pricing)

        td_list = browser.find_elements_by_tag_name('td')
        discount_exists = any(td.text == 'Discount:' for td in td_list)
        
        while discount_exists == False:
            supplemental_select = Select(browser.find_element_by_id('ddlAddSupplementals'))
            supplemental_select.select_by_value('55')
            add_button = browser.find_element_by_id('btnAddSupplemental')
            add_button.click()
            td_list = browser.find_elements_by_tag_name('td')

        base_retail = browser.find_element_by_id('ctl00_BodyContent_tbxShippingAmtBilled').get_attribute('value')

        if is_costco:
            discount = 0
            # discount = costco_discount(consignee_city, pallets, base_retail)
        else:
            discount = str(float(base_retail) * -0.0415)

        discount_box_pos = [td.text for td in td_list].index('Discount:')
        # input box in next TD cell after Discount label
        discount_cell = td_list[discount_box_pos + 1]
        discount_input = discount_cell.find_element_by_tag_name('input')
        discount_input.send_keys(Keys.CONTROL + 'a')
        discount_input.send_keys(Keys.DELETE)
        discount_input.send_keys(discount)

        save_button = browser.find_element_by_id('btnUpdateCosts')
        save_button.click()
        logging.info(load_id + ' discounted by ' + discount)
    except Exception as e:
        logging.exception(load_id + ' threw ' + repr(e))

browser.quit()
print('Browser closed.')