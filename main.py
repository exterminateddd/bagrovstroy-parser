from bs4 import BeautifulSoup
from urllib import request
from requests import get
from BSProject import Project
from pprint import pprint
from csv import DictWriter, writer, reader
import lxml


def parse_inner(link_inner):
    proj = Project()
    proj.price_vars = []
    proj.additional_options = []
    html_inner = get(link_inner, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}).text
    # print(html_inner)
    bs_inner = BeautifulSoup(html_inner, features="lxml")
    proj.name = bs_inner \
        .find('body') \
        .find('div', class_="breadcrumbs-block") \
        .find('div', class_="wrapper cf") \
        .find('div', class_="breadcrumbs") \
        .find('h1').text
    descr = bs_inner \
        .find('body') \
        .find('div', class_='main') \
        .find('div', class_='project__main') \
        .find('div', class_='project__descr_wrapper') \
        .find('div', class_="project__descr")
    for item in descr.find_all('div'):
        data = {
            'header': '',
            'prices': []
        }
        if item.find('div', class_='header'):
            data['header'] = item.find('div', class_='header').text
            if data['header'] == "Характеристики": continue
        else:
            continue
        for bl in item.find_all('div', class_='project__price_block'):
            block_data = {}
            block_data['size'] = bl.find('div', class_='left').find('div', class_='size').text
            block_data['price'] = bl.find('div', class_='right').find('div', class_='price').text
            data['prices'].append(block_data)
        proj.price_vars.append(data)

    proj.details = {}

    details = [
        i
        .find('div', class_='details')
        .find('div', class_='digit')
        .text
        for i in
        bs_inner.find('body')
        .find('div', class_='main')
        .find('div', class_='project__main')
        .find('div', class_='project__descr_wrapper')
        .find('div', class_='project__descr')
        .find('div', class_='descr_item__width')
        .find('div', class_='project__spec')
        .find_all('div', class_='project__spec_item')
    ]
    for k, v in zip(['Площадь', 'Размер', 'Комнаты', 'Этажность'], details):
        proj.details[k] = v

    add_opts = bs_inner.find('body') \
        .find('div', class_='main') \
        .find('div', id='more-extras') \
        .find_all('div')[5] \
        .find('div', class_='extras_table__body') \
        .find_all('label', class_='extras_table__body_row')

    for opt in add_opts:
        data = {
            'name': opt.find('div', class_='name').text,
            'price': opt.find('div', class_='price').text
        }
        proj.additional_options.append(data)

    return proj


def parse(link):
    items = []
    html = get(link, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}).text
    bs = BeautifulSoup(html, features="lxml")
    projects = [el.find('div', class_="project-item").find_all('a', href=True)[0]['href'] for el in
                bs
                    .find('body')
                    .find('div', class_="projects-block")
                    .find_all('div', class_="pr-wrapper")
                ]
    for proj in projects:
        items.append(parse_inner(proj))

    return [i.__dict__ for i in items]


file = open('data.csv', 'w+', encoding="utf8")
writer_ = writer(file)
data = parse('https://bagrovstroy.ru/')
writer_.writerow(
    ['Наименование',
     'Площадь',
     'Размер',
     'Комнаты',
     'Этажность',
     '90х140',
     '140x140',
     '190x140',
     '90х140 отд.',
     '140x140 отд.',
     '190x140 отд.',
     *[i['name'] for i in data[0]['additional_options']]
     ])
for p in data:
    writer_.writerow([p['name'].split(' ')[-1],
                      *[v for k, v in p['details'].items()],
                      *[j['price'] for j in p['price_vars'][0]['prices']],
                      *[j['price'] for j in p['price_vars'][1]['prices']],
                      *[i['price'] for i in p['additional_options']]
                      ])
file.close()
