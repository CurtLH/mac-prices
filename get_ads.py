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

# load credentials
with open("/home/curtis/credentials.json") as f:
    creds = json.load(f)

# connect to the database
try:
    conn = psycopg2.connect(database=creds["database"],
                            user=creds["user"],
                            password=creds["password"],
                            host=creds["host"])

    conn.autocommit = True
    cur = conn.cursor()
    logging.info("Successfully connected to the database")

except:
    logging.info("Unable to connect to the database")

# create the table to store the results
cur.execute("""CREATE TABLE IF NOT EXISTS apple_refurb_raw
               (id SERIAL,
                datetime timestamp default current_timestamp,
                url varchar,
                html varchar);""")

# get the URLs for all of the ads
urls = []
r = requests.get("https://www.apple.com/shop/refurbished/mac/macbook-pro")
soup = bs(r.content, "html.parser")
ads = soup.find("div",{"class":"refurbished-category-grid-no-js"})
for a in ads.find_all('a', href=True):
    url = "https://www.apple.com" + a['href'].split('?')[0]
    urls.append(url)
logging.info("URLs obtained: {}".format(len(urls)))

# collect content on the webpage for each URL
cnt = 0
    
for url in urls:
    r = requests.get(url)
    if r.status_code == 200:
        cur.execute("""INSERT INTO apple_refurb_raw (url, html)
                       VALUES (%s)""", [url, r.text])
        logging.info("New record inserted into database")
        cnt += 1
    
    else:
        #print("Record not inserted into database")
        pass
        
logging.info("New records collected: {}".format(cnt))
