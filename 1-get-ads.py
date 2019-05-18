import logging
import os
import psycopg2
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import json

# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


try:

    # connect to the database
    conn = psycopg2.connect(database="ads",
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
cur.execute("""CREATE TABLE IF NOT EXISTS refurb_mac 
               (id serial,
                datetime timestamp,
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
logging.info(len(urls), "URLs obtained")

# collect data for each URL
for url in urls:
    r = requests.get(url)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if r.status_code == 200:

        # put relevant info into a dictionary
        data = {}
        data['datetime'] = now
        data['url'] = url        
        data['response']= r.content.decode('utf-8')

        # convert dictionary to JSON
        response = json.dumps(data)

        # insert record into database
        cur.execute("INSERT INTO refurb_mac (datetime, response) VALUES (%s, %s)", [now, response])
        logging.info("New record inserted into database")
