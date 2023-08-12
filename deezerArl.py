import json, os

from time import sleep
from fake_useragent.fake import UserAgent
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

field_ids = {
    'gdpr': 'gdpr-btn-accept-all',
    'username': 'login_mail',
    'password': 'login_password',
    'button': 'login_form_submit'
}

def _get_arl(deezer):
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('log-level=3')

    driver = Edge(options=options, executable_path=os.path.join(os.getcwd(), "msedgedriver.exe"))
    driver.minimize_window()
    driver.get("https://www.deezer.com/en/login")

    sleep(0.1)

    driver.find_element(value=field_ids['gdpr']).click()

    if (not deezer['manual']):
        sleep(0.1)

        driver.find_element(value=field_ids['username']).send_keys(deezer['username'])
        driver.find_element(value=field_ids['password']).send_keys(deezer['password'])

        sleep(0.1)

        driver.find_element(value=field_ids['button']).click()

    driver.maximize_window()
    try:
        wait = WebDriverWait(driver, 600)
        wait.until(lambda driver: driver.current_url == "https://www.deezer.com/en/")
    except TimeoutException:
        return False
    sleep(0.1)

    cookies = driver.get_cookies()

    for x in cookies:
        if x['name'] == 'arl':
            driver.quit()
            return x['value']

    driver.quit()
    return False

def get_arl():
    with open("config.json") as json_data_file:
        config = json.load(json_data_file)

    if (config['username'] and config['username'] != "" and config['password'] and config['password'] != ""):
        manual = False

    thisArl = _get_arl({
        'manual': manual,
        'username': config['username'],
        'password': config['password'],
    })

    if (thisArl != False):
        return thisArl
    else:
        return get_arl(manual=manual)