import requests
from bs4 import BeautifulSoup
from pprint import pprint

import pymongo
from pymongo import MongoClient
from pymongo.errors import *

client = MongoClient('127.0.0.1', 27017)

# try:
#     client['HH_base'].vacancy.drop()
# except:
#     pass

db = client['HH_base']
hh_vacancy = db.vacancy
# hh_vacancy.delete_many({})
hh_vacancy.create_index([('tag', pymongo.TEXT)], name='search_index', unique=True)

page = 0
id = 0

running = True
while running:

    url = 'https://hh.ru'
    params = {'text': 'python', 'page': page, 'items_on_page': 20}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'}

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    try:
        next = dom.find('div', {'class': ['pager']}).find('a', {'class': ['bloko-button']}).get('href')
    except:
        running = False

    vacancies = dom.find_all('div', {'vacancy-serp-item'})

    list_of_vacancies = []

    for vacancy in vacancies:
        vacancy_data = {}
        name = vacancy.find('a').text.replace(' ', '_')
        link = vacancy.find('a', {'class': ['bloko-link']}).get('href')
        tag = ''

        for word in link:
            if word.isnumeric():
                tag = tag + word

        try:
            price = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).find('span').text.replace('\u202f', ' ')
            price_str = price[-4:].replace(' ', '')
            price = price[:-4]
            if '–' in price:
                price_list = price.split('–')
                price_min = int(price_list[0].replace(' ', ''))
                price_max = int(price_list[1].replace(' ', ''))
            elif 'от' in price:
                price_min = int(price[2:].replace(' ', ''))
                price_max = None
            elif 'до' in price:
                price_min = None
                price_max = int(price[2:].replace(' ', ''))
        except:
            price = None
            price_str = None
            price_min = None
            price_max = None

        id += 1

        vacancy_data['name'] = name
        vacancy_data['price_min'] = price_min
        vacancy_data['price_max'] = price_max
        vacancy_data['price_str'] = price_str
        vacancy_data['link'] = link
        vacancy_data['base'] = url
        vacancy_data['id'] = id
        vacancy_data['tag'] = tag
        # list_of_vacancies.append(vacancy_data)
        try:
            hh_vacancy.insert_one(vacancy_data)
        except DuplicateKeyError as double_error:
            print('Doublicate: ', double_error)
        # pprint(hh_vacancy.find_one({'tag': tag}))
    # pprint(list_of_vacancies)
    page += 1

# for doc in hh_vacancy.find({}):
#     pprint(doc)

price = 800000

for doc in hh_vacancy.find({'$or': [{'price_min': {'$gt': price}}, {'price_max': {'$gt': price}}]}):
    pprint(doc)
