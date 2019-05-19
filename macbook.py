import requests
from bs4 import BeautifulSoup as bs
from collections import defaultdict


def _get_specs(soup):

    specs = defaultdict(list)
    section = soup.find("div",{"class":"as-productinfosection-panel TechSpecs-panel row"})
    for cat in section.select('.h4-para-title'):
        k = cat.text.strip()
        for item in cat.find_next_siblings():
            if item.name != 'div':
                break
            else:
                specs[k.lower()].append(item.text.strip().lower())

    return dict(specs)


def _get_price(soup):

    price = soup.find("div",{"class":"as-price-currentprice as-pdp-currentprice as-pdp-refurbishedprice"})
    price = price.findAll('span')[0]
    price = price.getText().replace("\n", "").strip()
    price = price.replace('$', '').replace(',', '')
    price = float(price)

    return price


def _get_date(soup):

    specs = soup.find("div",{"class":"as-productinfosection-mainpanel column large-9 small-12"})
    for tag in specs.findAll('p'):
        parsed = tag.getText()
        if 'released' in parsed:
            date = parsed.replace("\n", "").strip().lower()
            break
        else:
            date = ""

    return date


def _get_screen(soup):

    specs = soup.find("div",{"class":"as-productinfosection-mainpanel column large-9 small-12"})
    for tag in specs.findAll('p'):
        parsed = tag.getText()
        if '-inch' in parsed.lower() and not parsed.startswith('http'):
            screen = parsed.replace("\n", "").strip().lower()
            break
        else:
            screen = ""

    return screen.strip().lower()


def _get_color(url):

    if 'space-gray' in url.lower():
        return 'space-gray'
    elif 'silver' in url.lower():
        return 'silver'
    else:
        return 'N/A'


def _get_id_num(url):

     return url.split('/')[5].lower()


def get_details(url):

    r = requests.get(url)
    if r.status_code == 200:
        soup = bs(r.content.decode('utf-8'), 'html.parser')
        specs = _get_specs(soup)
        specs['url'] = url
        specs['price'] = _get_price(soup)
        specs['date'] = _get_date(soup)
        specs['screen'] = _get_screen(soup)
        specs['id_num'] = _get_id_num(url)
        specs['color'] = _get_color(url)
        return specs

    else:
        raise ValueError("Failed to retrive URL")