def login(url, boolheadless=True):
    # activate headless mode
    options = Options()
    options.headless = boolheadless

    # activate chrome driver
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    # page elements to login
    boa_user = browser.find_element_by_id("txb-username")
    boa_pw = browser.find_element_by_id("txb-password")
    login_button = browser.find_element_by_id("ctl00_ContentBody_butLogin")

    # login credentials
    boa_user.send_keys("daigo@boalogistics.com")
    boa_pw.send_keys("ship12345")
    login_button.click()
    return browser

def run_lcr(load_list):
    base_url = 'https://boa.3plsystemscloud.com/'
    browser = tms.login(base_url, False)

    PREFIX = 'ctl00_BodyContent_'

    for load_id in loadlist:
        try:
            url = f'{base_url}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
            browser.get(url)

            # assign carrier
            lcr_carrier_link = browser.find_element_by_id(f'{PREFIX}hlCarrierLCRLink')
            lcr_carrier_link.click()
        
            # volume carrier only check
            volume_only = len(browser.find_elements(By.ID, f'{PREFIX}LineVolumeDiv'))
        
            if volume_only:
                print(load_id + ' is volume only')
            else:
                # wait until the rate table populates and becomes clickable
                WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, f'{PREFIX}objRateEngine_gvRates_ctl02_lnkQuoteNow')))

                # carrier filter logic
                rows = browser.find_elements_by_css_selector('tr.select-tooltip')
                buttons = browser.find_elements_by_css_selector('a.button-link')

                button_index = ''

                for y in rows:
                    row_index = rows.index(y)
                    carrier_name = rows[row_index].get_attribute('title')
                    
                    # carrier filters; if enabling or disabling, modify IF block below
                    roadrunner_check = carrier_name.lower().find('roadrunner') < 0
                    clearlane_check = carrier_name.lower().find('clear lane') < 0
                    frontline_check = carrier_name.lower().find('frontline') < 0
                    tradeshow_check = carrier_name.lower().find('trade show') < 0
                    overnite_check = carrier_name.lower().find('best overnite') < 0
                    central_check = carrier_name.lower().find('central freight') < 0
                    custom_check = carrier_name.lower().find('custom companies') < 0
                    
                    if tradeshow_check and frontline_check and clearlane_check and overnite_check and custom_check and roadrunner_check and central_check:
                        button_index = row_index * 2
                        break 

                buttons[button_index].click()
                WebDriverWait(browser, timeout=30).until(EC.element_to_be_clickable((By.ID, f'{PREFIX}divCarrierInfo')))
                carrier_info = browser.find_element_by_xpath(f"//div[@id='{PREFIX}divCarrierInfo']/div[1]/strong").text

                print(load_id)
                print(carrier_info)
                with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
                    carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    carrier_writer.writerow([load_id, carrier_info])
        except Exception as e:
            print(load_id + ' threw ' + repr(e))
            with open('lcr-carrier-list.csv', mode='a+') as carrier_list:
                carrier_writer = csv.writer(carrier_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                carrier_writer.writerow([load_id, repr(e)])

    browser.quit()

def book():
    pass

def dispatch():
    pass

class Truck:
    """
    Class to hold all information for the Married / Master truck.
    Object instance should be the truck number (truck1, truck2, etc.)
    """
    def __init__(self, married_load, carrier, dispatched):
        self.married_load = married_load
        self.carrier = carrier
        self.dispatched = dispatched

class Load:
    """
    Class to hold all load information
    """
    def __init__(self, load_id, whatelse):
        self.id = load_id
        self.whatelse = pass
        