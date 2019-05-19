import logging
import os
import json
import psycopg2
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from datetime import datetime

# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

# connect to the databse
try:

    # connect to the database
    conn = psycopg2.connect(database="postgres",
                            user=os.environ['PSQL_USER'],
                            password=os.environ['PSQL_PASSWORD'],
                            host=os.environ['PSQL_HOST'])

    # enable autocommit
    conn.autocommit = True

    # define the cursor to be able to write to the database
    cur = conn.cursor()
    logging.info("Successfully connected to the database")

except:
    logging.info("Unable to connect to the database")


# get the data from the table
cur.execute("""SELECT response, datetime, hash
               FROM mac_refurb_raw;""")
items = [line for line in cur]
logging.info("Number of ads to parse: {}".format(len(items)))

# iterate over each response and pull out information
clean = []
for line in items:
    soup = bs(line[0]['response'], "html.parser")
    specs = get_details(soup)
    specs['date_collected'] = datetime.strftime(line[1], '%Y-%m-%d %H:%m:%S')
    specs['url'] = line[0]['url']
    specs['id_num'] = line[0]['url'].split('/')[5]
    specs['color'] = get_color(line[0]['url'].lower())
    specs['hash'] = line[2]
    clean.append(specs)

# create a table to write clean results to
cur.execute("""CREATE TABLE IF NOT EXISTS mac_refurb
               (id SERIAL,
                datetime timestamp,
                hash uuid UNIQUE NOT NULL,
                details jsonb);""")

# load the data into the database
for line in clean:

    try:
        cur.execute("""INSERT INTO mac_refurb (datetime, hash, details)
                       VALUES (%s, %s, %s)""", [line['date_collected'], line['hash'], json.dumps(line)])
        logging.info("New records inserted into the database")

    except:
        pass
