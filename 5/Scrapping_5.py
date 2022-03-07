import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['mail']
mail = db.new
try:
    mail.delete_many({})
except Exception as E1:
    print('E1: ', E1)

chrome_options = Options()
# options.add_argument('--windows-size=100,720') # обе опции не работают почему-то
chrome_options.add_argument("--start-maximized") # обе опции не работают почему-то

driver = webdriver.Chrome('/Users/vadimmonroe/Desktop/Programming/_PROJECTS/DZ/SCRAPPING/1/5_selenium//chromedriver',
                          options=chrome_options)

wait = WebDriverWait(driver, 10)

driver.get('https://mail.ru')

# ------------------- логинимся -------------------
login = driver.find_element(By.CLASS_NAME, 'email-input')
login.send_keys('study.ai_172')
login = driver.find_element(By.XPATH, "//button[@class='button svelte-1tib0qz']")
login.click()
time.sleep(1)
login = driver.find_element(By.XPATH, "//input[@class='password-input svelte-1tib0qz']")
login.send_keys('NextPassword172#')
login.send_keys(Keys.ENTER)

wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dataset__items')]")))

# ------------------- смотрим сколько всего писем -------------------
all_button = driver.find_element(By.CLASS_NAME, 'button2__wrapper')
all_button.click()
count_mail = int(driver.find_element(By.CLASS_NAME, 'button2__txt').text)
print('Всего писем:', count_mail)
all_button.click()

real_count = 0
list_of_news = []
list_of_object_news = []
id = 0

while real_count < count_mail:
    content = driver.find_elements(By.CLASS_NAME, "js-tooltip-direction_letter-bottom")
# ------------------- Проходимся по письмам -------------------
    for item in content:
        new_item = {}
        if item not in list_of_object_news:
            list_of_object_news.append(item)
            email = item.find_element(By.CLASS_NAME, 'll-crpt').text
            date = item.find_element(By.CLASS_NAME, 'llc__item_date').text
            topic = item.find_element(By.CLASS_NAME, 'll-sj__normal').text
            link = item.get_attribute('href')
            id += 1

            new_item['email'] = email
            new_item['date'] = date
            new_item['topic'] = topic
            new_item['link'] = link
            new_item['id'] = id
            list_of_news.append(new_item)

# ------------------- листаем страницу вниз -------------------
    real_count = len(list_of_news)

    # content[-1].send_keys(Keys.PAGE_DOWN) - как вариант
    action = ActionChains(driver)
    action.move_to_element(content[-1])
    action.perform()

# ------------------- Переходим по ссылкам и добавляем в БД монго -------------------
for item in list_of_news:
    driver.get((item['link']))
    # почемуто не ждёт всей загрузки, и wait.until не помог, пришлось применить time.sleep
    # wait.until(EC.presence_of_element_located((driver.find_element(By.XPATH, '//body'))))
    time.sleep(3)
    text = driver.find_element(By.XPATH, '//div[contains(@class, "letter__body")]').text
    item['text'] = text
    print(item)
    mail.insert_one(item)

for doc in mail.find({}):
    pprint(doc)

driver.quit()
