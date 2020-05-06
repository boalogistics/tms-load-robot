import tms_login_ff as tms
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

# put FOR loop here to loop through list of load numbers
loadlist = ['150779']

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
