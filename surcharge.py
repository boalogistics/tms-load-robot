import logging
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


def get_discount(df_row, price):
    consignee_name = df_row['Consignee'].upper()
    consignee_city = df_row['C/ City']
    pallets = df_row['Pallets']
    is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in costco_discount_dict and pallets < 11
    if is_costco:
        discount_amt = calc_costco_discount(consignee_city, pallets, price)
    else:
        discount_amt = float(price) * -0.02
    return discount_amt


def add_surcharge(load, WebdriverObject, charge, surcharge_amt=0):
    surcharge_type = {
        'extreme_stir': ['Extreme Weather','298'],
        'dedicated': ['Dedicated Truck','241'],
        'extreme': ['PLACEHOLDER', '2']
    }
    
    surcharge = surcharge_type[charge]

    try:
        td_list = WebdriverObject.find_elements_by_tag_name('td')
        surcharge_exists = any(td.text == surcharge[0] for td in td_list)
        while not surcharge_exists:
            supplemental_select = Select(WebdriverObject.find_element_by_id('ddlAddSupplementals'))
            try:
                supplemental_select.select_by_value(surcharge[1])
            except Exception as e:
                logging.exception(f'{load} threw {repr(e)}')
            add_button = WebdriverObject.find_element_by_id('btnAddSupplemental')
            add_button.click()
            logging.info(f'Added invoice line {surcharge[0]}')
            td_list = WebdriverObject.find_elements_by_tag_name('td')
            surcharge_exists = any(td.text == surcharge[0] for td in td_list)
        if surcharge_amt:
            surcharge_box_pos = [td.text for td in td_list].index(surcharge[0])
            # input box in next TD cell after {SURCHARGE} label
            surcharge_cell = td_list[surcharge_box_pos + 1]
            surcharge_input = surcharge_cell.find_element_by_tag_name('input')
            surcharge_input.send_keys(Keys.CONTROL + 'a')
            surcharge_input.send_keys(Keys.DELETE)
            surcharge_input.send_keys(str(surcharge_amt))
            logging.info(f'{load} additional surcharge {surcharge[0]} {surcharge_amt}')
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')