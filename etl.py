import logging
import json
import psycopg2
from bs4 import BeautifulSoup as bs
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
cur.execute("""CREATE TABLE IF NOT EXISTS apple_refurb
               (id SERIAL,
                datetime timestamp default current_timestamp,
                url varchar,
                id_num varchar,
                price int,
                date varchar,
                screen varchar,
                color varchar);""")


# get the raw HTML data
cur.execute("""SELECT * 
               FROM apple_refurb_raw
               WHERE ID not in (SELECT id FROM apple_refurb);""")
raw = [line for line in cur]
logging.info("{} records obtained to load".format(len(raw)))

# exact info from each raw record
for line in raw:

    soup = bs(line[3], "html.parser")
    url = line[2]

    cur.execute("""INSERT INTO apple_refurb (url, id_num, price, date, screen, color)
                   VALUES (%s, %s, %s, %s, %s, %s)""", [line[2], 
                                                        macbook.get_id_num(url),
                                                        macbook.get_price(soup),
                                                        macbook.get_date(soup),
                                                        macbook.get_screen(soup),
                                                        macbook.get_color(url)
                                                       ])

    logging.info("New record inserted into database")
