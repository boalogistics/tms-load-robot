import csv
import tms_login as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# put FOR loop here to loop through list of load numbers
loadlist = [
]

for x in loadlist:
    try:
        load_id = x
        url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
        browser.get(url)

        WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_anchor_Editpricing')))

        table = browser.find_element_by_id('ctl00_BodyContent_tblCommodities')

        rowslist = table.find_elements_by_tag_name('tr')
        pricerow = str(len(rowslist)-1)
        marginrow = str(len(rowslist))
        # print(len(rowslist))
        # print(rowslist[len(rowslist)-1].text)
        # print(rowslist[len(rowslist)-2].text)

        def get_price(row, column):
            price = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + row +"]/td[@class='GridDataRight'][" + str(column) + "]").text
            return price

        cost = get_price(pricerow, 3)
        billed = get_price(pricerow, 2)
        margin_usd = get_price(marginrow, 3)
        margin_pct = get_price(marginrow, 2)

        # cost = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + pricerow +"]/td[@class='GridDataRight'][3]").text
        # billed = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + pricerow +"]/td[@class='GridDataRight'][2]").text
        # margin_usd = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + marginrow +"]/td[@class='GridDataRight'][3]").text
        # margin_pct = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + marginrow +"]/td[@class='GridDataRight'][2]").text
        
        print('Load: ' + load_id + ', Cost: ' + cost + ', Billed: ' + billed + ', Margin$: ' + margin_usd + ', Margin%: ' + margin_pct)
        
        with open('pricing.csv', mode='a+') as pricing:
            price_writer = csv.writer(pricing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            price_writer.writerow([load_id, cost, billed, margin_usd, margin_pct])
    except Exception as e:
        print(load_id + ' threw ' + repr(e))
        with open('pricing.csv', mode='a+') as pricing:
            price_writer = csv.writer(pricing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            price_writer.writerow([load_id, cost, billed, margin_usd, margin_pct])
          
browser.quit()

# def carrier_filter(carrier_dict):
#         for key in carrier_dict:
#             carrier_dict[key] = carrier_name.lower().find(key) < 0