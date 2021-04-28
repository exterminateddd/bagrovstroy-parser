from bs4 import BeautifulSoup
from urllib import request
from requests import get
from BSProject import Project
from pprint import pprint
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

    add_opts = bs_inner.find('body') \
          .find('div', class_='main')\
          .find('div', id='more-extras')\
          .find_all('div')[5]\
          .find('div', class_='extras_table__body')\
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

    with request.urlopen(link) as response:
        html = response.read().decode('utf-8')
    bs = BeautifulSoup(html, features="html.parser")
    projects = [el.find('div', class_="project-item").find_all('a', href=True)[0]['href'] for el in
                bs
                    .find('body')
                    .find('div', class_="projects-block")
                    .find_all('div', class_="pr-wrapper")
                ]
    for proj in projects[:5]:
        items.append(parse_inner(proj))

    return [i.__dict__ for i in items]


pprint(parse("https://bagrovstroy.ru/catalog"))