import logging, logging.config
import tms_login as tms

# initialize logger
logging.config.fileConfig(fname='logs/cfg/upload.conf')
logger = logging.getLogger('')

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

load_list = ['154615',
'154680',
'154989',
'155097',
'155105',
'155701',
'155747',
'155774',
'155842',
'155855',
'155867',
'155890',
'155892',
'155967',
'155990',
'156009',
'156079',
'156085',
'156096',
'156101',
'156120',
'156194',
'156237',
'156240',
'156251',
'156257',
'156274',
'156276',
'156309',
'156343',
'156347',
'156350',
'156367',
'156369',
'156394',
'156410',
'156431',
'156433',
'156469',
'156495',
'156535',
'156540',
'156603',
'156605',
'156605',
'156621',
'156626',
'157653',
'157826',
'157860',
'157883',
'157927',
'157969',
'157970',
'158872',
'158940',
'158978',
'158986',
'158995',
'158999',
'159003',
'159004',
'159105',
'159161',
'159256',
'159257',
'159285',
'154610',
'155847',
'155847',
'155959',
'156143',
'156153',
'156254',
'156336',
'156393',
'156474',
'156496',
'157572',
'157574',
'157574',
'157835',
'157835'
]

for x in load_list:
    load_id = x

    upload = 'http://boa.3plsystemscloud.com/App_BW/staff/utilities/DocStorageAdd.aspx?loadid=' + load_id
    browser.get(upload)

    choose_file = browser.find_element_by_id('ctl00_BodyContent_fileUpLoadDoc')
    try:
        choose_file.send_keys('S:\\POD Folder\\' + load_id + '.pdf')
        upload_btn = browser.find_element_by_id('ctl00_BodyContent_btnUploadFile')
        upload_btn.click()
        logging.info('POD for ' + load_id + ' uploaded.')
    except Exception as e:
        logging.exception('POD for' + load_id + ' not uploaded: ' + repr(e))

browser.close()
print('Browser closed.')