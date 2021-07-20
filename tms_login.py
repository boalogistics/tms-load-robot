from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def login(url, boolheadless=True):
    # activate headless mode
    options = Options()
    options.headless = boolheadless
    options.add_argument('--remote-debugging-port=9222')
    options.binary_location = '/usr/bin/chromium-browser'
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

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
