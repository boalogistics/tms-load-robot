import tms_login as tms

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url)

load_list = ['156336', 
'156292', 
'154910', 
'156207', 
'155871', 
'155894', 
'156288', 
'155848', 
'156187', 
'156789', 
'156514'
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
        print('POD for ' + load_id + ' uploaded.')
    except Exception as e:
        print(load_id + ' threw ' + repr(e))

browser.close()
print('Browser closed.')