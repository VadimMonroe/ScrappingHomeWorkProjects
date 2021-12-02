import requests
from pprint import pprint
from lxml import html
import pymongo
from pymongo import MongoClient
from pymongo.errors import *

client = MongoClient('127.0.0.1', 27017)

db = client['Yandex_News']
y_news = db.news
y_news.delete_many({})
# hh_vacancy.create_index([('tag', pymongo.TEXT)], name='search_index', unique=True)


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'}
response = requests.get('https://yandex.ru/news/', headers=header)
dom = html.fromstring(response.text)

top = "//div[contains(@class, 'news-top')]"
regions = "//div[@class = 'mg-grid__row mg-grid__row_gap_8 mg-top-rubric-flexible-stories tD6ILDXGerw0__top']"

news_list = [top]

yandex_news = []

for news_place in news_list:
    news = dom.xpath(news_place)[0]

    for item in news:
        news = {}

        news_title = item.xpath(".//h2[contains(@class, 'mg-card__title')]")[0].text.replace(('\xa0'), (' '))
        news_link = item.xpath(".//h2[contains(@class, 'mg-card__title')]/../@href")[0]
        news_source = item.xpath(".//a[contains(@class, 'mg-card__source-link')]")[0].text
        news_time = item.xpath(".//span[contains(@class, 'mg-card-source__time')]")[0].text

        news['title'] = news_title
        news['link'] = news_link
        news['source'] = news_source
        news['time'] = news_time

        yandex_news.append(news)

        try:
            y_news.insert_one(news)
        except DuplicateKeyError as double_error:
            print('Doublicate: ', double_error)

for doc in y_news.find({}):
    pprint(doc)
