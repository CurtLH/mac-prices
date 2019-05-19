import logging
import os
import psycopg2
import requests
from bs4 import BeautifulSoup as bs
import json
import hashlib
import macbook

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# connect to the database
try:
    conn = psycopg2.connect(database="postgres",
                            user=os.environ['PSQL_USER'],
                            password=os.environ['PSQL_PASSWORD'],
                            host=os.environ['PSQL_HOST'])

    conn.autocommit = True
    cur = conn.cursor()
    logging.info("Successfully connected to the database")

except:
    logging.info("Unable to connect to the database")

# create the table to store the results
cur.execute("""CREATE TABLE IF NOT EXISTS mac_refurb
               (id SERIAL,
                datetime timestamp default current_timestamp,
                details jsonb,
                hash uuid UNIQUE NOT NULL);""")

# get the URLs for all of the ads
urls = []
r = requests.get("https://www.apple.com/shop/refurbished/mac/macbook-pro")
soup = bs(r.content, "html.parser")
ads = soup.find("div",{"class":"refurbished-category-grid-no-js"})
for a in ads.find_all('a', href=True):
    urls.append("https://www.apple.com" + a['href'])
logging.info("URLs obtained: {}".format(len(urls)))

# collect content on the webpage for each URL
for url in urls:
    specs = macbook.get_details(url)
    details = json.dumps(specs)
    md5 = hashlib.md5(details.encode('utf-8')).hexdigest()

    try:
        cur.execute("""INSERT INTO mac_refurb (url, details, hash)
                       VALUES (%s, %s, %s)""", [url, details, md5])
        logging.info("New record inserted into database")

    except:
        logging.info("Record not inserted into database")
        pass
