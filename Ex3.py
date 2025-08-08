import json
from time import sleep
from datetime import datetime
from functools import wraps

from selenium.common import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

def wait_element(browser, delay=1, by=By.TAG_NAME, value=None):
    try:
        return WebDriverWait(browser, delay).until(
            expected_conditions.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None

chrome_path = ChromeDriverManager().install()
service = Service(executable_path=chrome_path)
browser = Chrome(service=service)




def logger(old_function):
    @wraps(old_function)
    def new_function(*args, **kwargs):
        result = old_function(*args, **kwargs)


        log_message = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
            f"{old_function}\n"
            f"{args}\n"
            f"{kwargs}\n"
            f"{result}\n"
        )

        path = 'main.log'
        try:
            with open(path, 'a', encoding='utf-8') as file:
                file.write(log_message)
        except FileNotFoundError:
            with open(path, 'x', encoding='utf-8') as file:
                file.write(log_message)
        return result
    return new_function

@logger
def web_scraping(path, keywords):
    browser.get(path)
    sleep(2)

    link_list = []

    articles_list = browser.find_elements(by=By.CSS_SELECTOR, value='div.tm-article-snippet')
    for article in articles_list:
        link_element = wait_element(
            browser=article,
             by=By.CSS_SELECTOR,
            value='a.tm-title__link'
        )
        link = link_element.get_attribute('href')
        link_list.append(link)

    for link in link_list:
        browser.get(link)
        sleep(1)
        parsed_data = []
        title = (wait_element(
            browser,
            by=By.TAG_NAME,
            value='h1').text.strip())
        time = wait_element(browser,
                            by=By.TAG_NAME,
                            value='time').get_attribute('datetime')
        text = (wait_element(browser,
                            by=By.CLASS_NAME,
                            value='article-formatted-body').text.strip())
        for keyword in keywords:
            if keyword in text or keyword in title:
                parsed_data.append({'title': title,
                                    'time': time,
                                    'text': text})
                print(f'Found keyword "{keyword}" in the text of the article "{title}"')
                try:
                    with open('parsed data.txt', 'a', encoding='utf-8') as file:
                        file.write(json.dumps(parsed_data, ensure_ascii=False, indent=2))
                except FileNotFoundError:
                    with open('parsed data.txt', 'x', encoding='utf-8') as file:
                        file.write(json.dumps(parsed_data, ensure_ascii=False, indent=2))
                break

    return None



if __name__ == '__main__':
    keywords = ['дизайн', 'фото', 'web', 'python']
    path = 'https://habr.com/ru/articles/'
    web_scraping(path, keywords)