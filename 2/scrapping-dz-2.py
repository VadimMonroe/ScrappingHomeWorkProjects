import requests
from bs4 import BeautifulSoup
from pprint import pprint

page = 0
id = 0
running = True
while running:

    url = 'https://hh.ru'
    params = {'text': 'python', 'page': page}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'}

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    try:
        next = dom.find('div', {'class': ['pager']}).find('a', {'class': ['bloko-button']}).get('href')
    except:
        running = False
        break

    vacancies = dom.find_all('div', {'vacancy-serp-item'})

    list_of_vacancies = []

    for vacancy in vacancies:
        vacancy_data = {}
        name = vacancy.find('a').text
        link = vacancy.find('a', {'class': ['bloko-link']}).get('href')
        try:
            price = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).find('span').text.replace('\u202f', ' ')
            price_str = price[-4:]
            price = price[:-4]
            if '–' in price:
                price_list = price.split('–')
                price_min = price_list[0]
                price_max = price_list[1]
            else:
                price_min = price
                price_max = None
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
        list_of_vacancies.append(vacancy_data)
    pprint(list_of_vacancies)
    page += 1
