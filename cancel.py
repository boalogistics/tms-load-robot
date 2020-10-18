import logging, logging.config, time
import tms_login as tms

# initialize logger
logging.config.fileConfig(fname='logger.conf')
logger = logging.getLogger('')


url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)


load_list = ['159971',
'159972',
'159973',
'159974',
'159975',
'159976',
'159977',
'159978',
'159979',
'159980',
'159981',
'159982',
'159983',
'159984',
'159985',
'159986',
'159987',
'159988',
'159989',
'159990',
'159991',
'159992',
'159993',
'159994',
'159995',
'159996']

for load_id in load_list:
    load_url = f'{url}App_BW/staff/shipment/shipmentDetail.aspx?loadid={load_id}'
    browser.get(load_url)

#    js_cancel = 'WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$BodyContent$lbCancel&quot;, &quot;&quot;, true, &quot;&quot;, &quot;&quot;, false, true))'
#    browser.execute_script(js_cancel)
    cancel = browser.find_element_by_id('ctl00_BodyContent_spnCancel')
    cancel.click()
    alert = browser.switch_to.alert
    alert.accept()
    time.sleep(3)
    logging.info(load_id + ' cancelled.')

browser.quit()

print('Browser closed.')