import json
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import csv

########################
### HELPER FUNCTIONS ###
########################

def get_specs(soup):

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


def get_price(soup):

    price = soup.find("div",{"class":"as-price-currentprice as-pdp-currentprice as-pdp-refurbishedprice"})
    price = price.findAll('span')[0]
    price = price.getText().replace("\n", "").strip()
    price = price.replace('$', '').replace(',', '')
    price = float(price)

    return price


def get_date(soup):

    specs = soup.find("div",{"class":"as-productinfosection-mainpanel column large-9 small-12"})
    for tag in specs.findAll('p'):
        parsed = tag.getText()
        if 'released' in parsed:
            date = parsed.replace("\n", "").strip().lower()
            break
        else:
            date = ""

    return date


def get_screen(soup):

    specs = soup.find("div",{"class":"as-productinfosection-mainpanel column large-9 small-12"})
    for tag in specs.findAll('p'):
        parsed = tag.getText()
        if '-inch' in parsed.lower() and not parsed.startswith('http'):
            screen = parsed.replace("\n", "").strip().lower()
            break
        else:
            screen = ""

    return screen


def get_color(url):

    if 'space-gray' in url:
        return 'space-gray'
    elif 'silver' in url:
        return 'silver'
    else:
        return 'N/A'


def get_details(soup):

    specs = get_specs(soup)
    specs['price'] = get_price(soup)
    specs['date'] = get_date(soup)
    specs['screen'] = get_screen(soup).strip().lower()


    return specs


####################
### MAIN PROGRAM ###
####################

# read in JSON data
with open('results.json') as f:
    data = json.load(f)

# iterate over each response and pull out information
clean = []
for line in data:
    soup = bs(data[line]['response'], "html.parser")
    specs = get_details(soup)
    specs['date_collected'] = data[line]['date_collected']
    specs['url'] = line
    specs['id_num'] = line.split('/')[5]
    specs['color'] = get_color(line.lower())
    clean.append(specs)

# format data
final = []
for line in clean:
    row = {
        'id': line['id_num'],
        'url': line['url'],
        'date': ' '.join(line['date'].split(' ')[2:]),
        'memory': ";".join(line['memory']).split(' ')[0],
        'storage': ";".join(line['storage']).split(' ')[0],
        'graphics': ";".join(line['graphics']),
        'price': line['price'],
        'color': line['color']
    }
    final.append(row)

# write results to a CSV file
with open('refurb_prices.csv', 'w') as f:
    writer = csv.DictWriter(f, final[0].keys())
    writer.writeheader()
    writer.writerows(final)
