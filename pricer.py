import tms_login as tms
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# put FOR loop here to loop through list of load numbers
loadlist = [
'156557', 
'157878', 
'156065', 
'156117', 
'156154', 
'156156', 
'156157', 
'156158', 
'156159', 
'156162', 
'157617', 
'156536', 
'156537', 
'157967', 
'157999', 
'156540', 
'157636', 
'157825', 
'156528', 
'156563', 
'156390', 
'155842', 
'155915', 
'156269', 
'155833', 
'156396', 
'156399', 
'156407', 
'156161', 
'156155', 
'156567', 
'156352', 
'156686', 
'158001', 
'157910', 
'156535', 
'156410', 
'157948', 
'156388', 
'156452', 
'156253', 
'155819', 
'156370', 
'157891', 
'157915', 
'156539', 
'156463', 
'156401', 
'156562', 
'156572', 
'156475', 
'157943', 
'157827', 
'155848', 
'155884', 
'150779', 
'154989', 
'157823', 
'156487', 
'156340', 
'156325', 
'157939', 
'157942', 
'157824', 
'157998', 
'157887', 
'156321', 
'157959', 
'156347', 
'155852', 
'155847', 
'156468', 
'156574', 
'157992', 
'158000', 
'156565', 
'157601'
]

for x in loadlist:
    try:
        og_window = browser.window_handles[0]
        
        load_id = x
        url = 'https://boa.3plsystemscloud.com/App_BW/staff/shipment/shipmentDetail.aspx?loadid='+load_id
        browser.get(url)

        WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, 'ctl00_BodyContent_anchor_Editpricing')))

        editpricing = browser.find_element_by_id('ctl00_BodyContent_anchor_Editpricing')
        editpricing.click()

        WebDriverWait(browser, timeout=30).until(EC.number_of_windows_to_be(2))
        popup = browser.window_handles[1]
        browser.switch_to.window(popup)

        supplemental_select = Select(browser.find_element_by_id('ddlAddSupplementals'))
        supplemental_select.select_by_value('55')

        add_button = browser.find_element_by_id('btnAddSupplemental')
        add_button.click()

        # WebDriverWait(browser, timeout=120).until(EC.element_to_be_clickable((By.ID, 'tbxAccessorialBilledNet55')))
        # discount = browser.find_element_by_id('tbxAccessorialBilledNet55')
        # discount.send_keys(Keys.CONTROL + 'a')
        # discount.send_keys(Keys.DELETE)
        # discount.send_keys(500)

        save_button = browser.find_element_by_id('btnUpdateCosts')
        save_button.click()

        browser.switch_to.window(og_window)
        
        # rowslist = table.find_elements_by_tag_name('tr')
        # pricerow = str(len(rowslist)-1)
        # marginrow = str(len(rowslist))
        # # print(len(rowslist))
        # # print(rowslist[len(rowslist)-1].text)
        # # print(rowslist[len(rowslist)-2].text)

        # cost = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + pricerow +"]/td[@class='GridDataRight'][3]").text
        # billed = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + pricerow +"]/td[@class='GridDataRight'][2]").text
        # margin_usd = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + marginrow +"]/td[@class='GridDataRight'][3]").text
        # margin_pct = browser.find_element_by_xpath("//table[@id='ctl00_BodyContent_tblCommodities']/tbody/tr[" + marginrow +"]/td[@class='GridDataRight'][2]").text
        
        # print('Load: ' + load_id + ', Cost: ' + cost + ', Billed: ' + billed + ', Margin$: ' + margin_usd + ', Margin%: ' + margin_pct)
        

    except Exception as e:
        print(load_id + ' threw ' + repr(e))
