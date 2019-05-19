import logging
import os
import psycopg2
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import json
import hashlib

# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# try to connect to the database
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

# create table for results
cur.execute("""CREATE TABLE IF NOT EXISTS mac_refurb_raw
               (id serial PRIMARY KEY,
                datetime timestamp default current_timestamp,
                hash uuid UNIQUE NOT NULL,
                response jsonb);""")
logging.info("Table created")

# get the URLs for all refurbished computers
urls = []
r = requests.get("https://www.apple.com/shop/refurbished/mac/macbook-pro")
soup = bs(r.content, "html.parser")
ads = soup.find("div",{"class":"refurbished-category-grid-no-js"})
for a in ads.find_all('a', href=True):
    urls.append("https://www.apple.com" + a['href'])

# print status
logging.info("URLs obtained: {}".format(len(urls)))

# collect data for each URL
for url in urls:
    r = requests.get(url)
    if r.status_code == 200:

        # put relevant info into a dictionary
        data = {}
        data['url'] = url        
        data['response']= r.content.decode('utf-8')

        # convert the dict to json
        response = json.dumps(data)

        # create a hash of the data
        md5 = hashlib.md5(response.encode('utf-8')).hexdigest()

	# try to insert the content into the database
        try:
            cur.execute("""INSERT INTO mac_refurb_raw (hash, response)
                           VALUES (%s, %s)""", [md5, response])
            logging.info("New record inserted into the database")

        except:
            logging.info("Duplicate record already exists")
