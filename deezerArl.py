import json, os

from time import sleep
# from fake_useragent.fake import UserAgent
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

def _get_arl(deezer, wait_time=0.5):
    options = Options()
    # ua = UserAgent()
    user_agent = "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'"
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('log-level=3')

    driver = Edge(options=options, executable_path=os.path.join(os.getcwd(), "msedgedriver.exe"))
    driver.minimize_window()
    driver.get("https://www.deezer.com/en/login")

    try:
        sleep(wait_time)

        driver.find_element(value=field_ids['gdpr']).click()

        if (not deezer['manual']):
            sleep(wait_time)

            driver.find_element(value=field_ids['username']).send_keys(deezer['username'])
            driver.find_element(value=field_ids['password']).send_keys(deezer['password'])

            sleep(wait_time)

            driver.find_element(value=field_ids['button']).click()

        driver.maximize_window()
        try:
            wait = WebDriverWait(driver, 600)
            wait.until(lambda driver: driver.current_url == "https://www.deezer.com/en/")
        except TimeoutException:
            return False
        sleep(wait_time)

        cookies = driver.get_cookies()

        for x in cookies:
            if x['name'] == 'arl':
                driver.quit()
                return x['value']

        driver.quit()
        return False
    except:
        driver.quit()
        return False

def get_arl(wait=0.5):
    with open("config.json") as json_data_file:
        config = json.load(json_data_file)

    thisArl = False
    if ('username' in config and config['username'] != "" and 'password' in config and config['password'] != ""):
        thisArl = _get_arl({
            'manual': False,
            'username': config['username'],
            'password': config['password'],
        }, wait_time=wait)
    else:
        thisArl = _get_arl({
            'manual': True,
        }, wait_time=wait)

    if (thisArl != False):
        return thisArl
    else:
        return get_arl(wait=wait + 1)