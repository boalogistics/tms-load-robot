import tms_login as tms
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def costco_discount(city, pallets, retail):
    # subtract 1 from pallets argument for list index
    discount_rate = discount_dict[city][pallets - 1]
    # round to nearest multiple of 5
    reduction_value = 5 * round(retail * discount_rate) / 5
    return reduction_value

discount_dict = {"West Palm Beach": [0.0294, 0.0466, 0.0542, 0.0601, 0.0593, 0.0595, 0.0546, 0.0570, 0.0471, 0.0379], 
                "Atlanta": [0.0288, 0.0457, 0.0549, 0.0597, 0.0595, 0.0610, 0.0559, 0.0573, 0.0473, 0.0377], 
                "Monrovia":[0.0294, 0.0444, 0.0541, 0.0610, 0.0608, 0.0598, 0.0557, 0.0576, 0.0477, 0.0372], 
                "Monroe Township": [0.0288, 0.0455, 0.0552, 0.0600, 0.0604, 0.0596, 0.0554, 0.0569, 0.0470, 0.0374]}   

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

loadlist = ['155819',
'156269',
'157825',
'155884',
'156162'
]

for x in loadlist:
    try:        
        load_id = x
        load_url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
        browser.get(load_url)

        consignee_name = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divShipRecLocations']/span/span[2]/div[@class='DivPanelB']/div[@class='PanelBodyForm']/table/tbody/tr[1]/td").text.upper()
        consignee_city = browser.find_element_by_xpath("//div[@id='ctl00_BodyContent_divShipRecLocations']/span/span[2]/div[@class='DivPanelB']/div[@class='PanelBodyForm']/table/tbody/tr[3]/td").text
        is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in discount_dict
        pallets = 'getpalletcount'

        # add pallet counter here
        # how to account for non discount costco locations?
        # run a report for costco?

        edit_pricing = 'http://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentCostPop.aspx?loadid='+load_id
        browser.get(edit_pricing)

        price_table = browser.find_element_by_id('tblPricing')
        price_elements = price_table.find_elements_by_tag_name('td')
        discount_exists = any(td.text == 'Discount:' for td in price_elements)
        
        while discount_exists == False:
            supplemental_select = Select(browser.find_element_by_id('ddlAddSupplementals'))
            supplemental_select.select_by_value('55')
            add_button = browser.find_element_by_id('btnAddSupplemental')
            add_button.click()
            discount_exists = any(td.text == 'Discount:' for td in price_elements)

        base_retail = browser.find_element_by_id('ctl00_BodyContent_tbxShippingAmtBilled').get_attribute('value')

        if is_costco:
            discount = 0
            # discount = costco_discount(consignee_city, pallets, base_retail)
        else:
            discount = str(float(base_retail) * -0.0415)

        discount_box_pos = [td.text for td in price_elements].index('Discount:')
        # input box in next TD cell after Discount label
        discount_cell = price_elements[discount_box_pos + 1]
        discount_input = discount_cell.find_element_by_tag_name('input')
        discount_input.send_keys(Keys.CONTROL + 'a')
        discount_input.send_keys(Keys.DELETE)
        discount_input.send_keys(discount)

        save_button = browser.find_element_by_id('btnUpdateCosts')
        save_button.click()
        print(load_id + ' discounted by ' + discount)
    except Exception as e:
        print(load_id + ' threw ' + repr(e))

browser.quit()
print('Browser closed.')