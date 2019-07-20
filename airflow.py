from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs

default_args = {
    'owner': 'curtis',
    'start_date': datetime(2019, 7, 19),
}

dag = DAG(
    'apples', default_args=default_args, schedule_interval='@daily')

def get_ads():

    urls = []
    r = requests.get("https://www.apple.com/shop/refurbished/mac/macbook-pro")
    soup = bs(r.content, "html.parser")
    ads = soup.find("div",{"class":"refurbished-category-grid-no-js"})
    for a in ads.find_all('a', href=True):
        url = "https://www.apple.com" + a['href'].split('?')[0]
        urls.append(url)

    conn = PostgresHook(postgres_conn_id = "postgres_default", schema="curtis").get_conn()
    conn.autocommit = True
    cur = conn.cursor()

    for url in urls[:10]:
        r = requests.get(url)
        if r.status_code == 200:
            cur.execute("""INSERT INTO apple_refurb_raw_2 (url, html)
                           VALUES (%s, %s)""", [url, r.text])

        else:
            pass

    cur.close()
    conn.close()

task = PythonOperator(
    task_id="get_ads",
    python_callable=get_ads,
    dag=dag
)
