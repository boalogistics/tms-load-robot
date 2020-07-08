import json
import logging
from math import ceil
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# Max weight to count as 1 chargeable pallet
MAX_WEIGHT = 1768
# Pallets exceeding will count as 2 chargeable plts
MAX_WEIGHT_2 = 2350
# Percent discount for pallet counts 1 to 10
discount_rates = [
    0.006, 0.0075, 0.0035, 0.0035, 0.0040,
    0.0045, 0.005, 0.0055, 0.006, 0.006
    ]
# look up df_row in json for Costco location x Pallets
costco_discount_dict = json.load(open('db/costco_table.json', 'r'))


def get_price(df_row):
    origin = df_row['S/ City'] + ', ' + df_row['S/ State']
    destination = df_row['C/ City'] + ', ' + df_row['C/ State']
    weight = df_row['Weight']
    pallets = df_row['Pallets']

    rate_df_row = pd.read_excel('db/stir.xlsx')
    key = json.load(open('db/region.json', 'r'))
    df = pd.DataFrame(rate_df_row)
    df = pd.pivot_df_row(df, index=['Origin', 'Destination'])
    base_selling = df.loc[key[origin]].loc[destination][pallets]

    wt_per_plt = weight / pallets

    if wt_per_plt <= MAX_WEIGHT:
        chgble_plt = 1
    elif wt_per_plt > MAX_WEIGHT_2:
        chgble_plt = 2
    else:
        chgble_plt = wt_per_plt / MAX_WEIGHT

    discount = discount_rates[pallets - 1]
    chargeable_selling = (chgble_plt * base_selling) * (1 - discount)

    if base_selling > chargeable_selling:
        return base_selling
    else:
        if pallets < 5:
            return ceil((chargeable_selling - 5) / 10) * 10
        else:
            return ceil((chargeable_selling / 10)) * 10


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


def get_discount(df_row, price):
    consignee_name = df_row['Consignee'].upper()
    consignee_city = df_row['C/ City']
    pallets = df_row['Pallets']
    is_costco = consignee_name.find('COSTCO') != -1 and consignee_city in costco_discount_dict and pallets < 11
    if is_costco:
        discount = calc_costco_discount(consignee_city, pallets, price)
    else:
        discount = price * -0.0415
    return discount


def apply_discount(load, discount, WebdriverObject):
    try:
        td_list = WebdriverObject.find_elements_by_tag_name('td')
        discount_exists = any(td.text == 'Discount:' for td in td_list)
        while not discount_exists:
            supplemental_select = Select(WebdriverObject.find_element_by_id('ddlAddSupplementals'))
            try:
                supplemental_select.select_by_value('55')
            except Exception as e:
                logging.exception(f'{load} threw {repr(e)}')
            add_button = WebdriverObject.find_element_by_id('btnAddSupplemental')
            add_button.click()
            td_list = WebdriverObject.find_elements_by_tag_name('td')
            discount_exists = any(td.text == 'Discount:' for td in td_list)

        discount_box_pos = [td.text for td in td_list].index('Discount:')
        # input box in next TD cell after Discount label
        discount_cell = td_list[discount_box_pos + 1]
        discount_input = discount_cell.find_element_by_tag_name('input')
        discount_input.send_keys(Keys.CONTROL + 'a')
        discount_input.send_keys(Keys.DELETE)
        discount_input.send_keys(str(discount))
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')
