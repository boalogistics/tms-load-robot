import json
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# look up table in json for Costco location x Pallets
costco_discount_dict = json.load(open('db/costco_table.json', 'r'))


def calc_costco_discount(city, pallets, retail):
    reduction_value = 0
    if pallets < 11:
        # subtract 1 from pallets argument for list index
        discount_rate = costco_discount_dict[city][pallets - 1]
        # round to nearest multiple of 5
        reduction_value = -5 * round(retail * discount_rate) / 5
    else:
        logging.info(f'{city} pallet count over 10, consult sales.')
    return reduction_value


def applydiscount(table, WebdriverObject):
    for x in table.index:
        try:
            load_id = str(table['Load #'][x])

            # how to deal with multistop?

            edit_pricing = f'http://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentCostPop.aspx?loadid={load_id}'
            WebdriverObject.get(edit_pricing)

            td_list = WebdriverObject.find_elements_by_tag_name('td')
            discount_exists = any(td.text == 'Discount:' for td in td_list)
            
            while not discount_exists:
                supplemental_select = Select(WebdriverObject.find_element_by_id('ddlAddSupplementals'))
                try:
                    supplemental_select.select_by_value('55')
                except Exception as e:
                    logging.exception(load_id + ' threw ' + repr(e))
                add_button = WebdriverObject.find_element_by_id('btnAddSupplemental')
                add_button.click()
                td_list = WebdriverObject.find_elements_by_tag_name('td')
                discount_exists = any(td.text == 'Discount:' for td in td_list)

            consignee_name = table['Consignee'][x].upper()
            consignee_city = table['C/ City'][x]
            pallets = table['Pallets'][x]
            is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in costco_discount_dict and pallets < 11
            base_retail = table['Base Retail'][x]

            if is_costco:
                discount = str(calc_costco_discount(consignee_city, pallets, base_retail))
            else:
                discount = str(base_retail * -0.0415)

            discount_box_pos = [td.text for td in td_list].index('Discount:')
            # input box in next TD cell after Discount label
            discount_cell = td_list[discount_box_pos + 1]
            discount_input = discount_cell.find_element_by_tag_name('input')
            discount_input.send_keys(Keys.CONTROL + 'a')
            discount_input.send_keys(Keys.DELETE)
            discount_input.send_keys(discount)

            save_button = WebdriverObject.find_element_by_id('btnUpdateCosts')
            save_button.click()
            logging.info(f'{load_id} base retail {base_retail} discounted {discount} ({float(discount)/base_retail})')
        except Exception as e:
            logging.info(load_id + ' threw ' + repr(e))
