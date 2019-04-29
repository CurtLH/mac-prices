import requests
from bs4 import BeautifulSoup as bs
import json

# get the URLs for all refurbished computers
urls = []
r = requests.get("https://www.apple.com/shop/refurbished/mac/macbook-pro")
soup = bs(r.content, "html.parser")
ads = soup.find("div",{"class":"refurbished-category-grid-no-js"})
for a in ads.find_all('a', href=True):
    urls.append("https://www.apple.com" + a['href'])

# print status
print(len(urls), "URLs obtained")

# collect data for each URL
data = {}
for url in urls:
    r = requests.get(url)
    if r.status_code == 200:
        data[url] = r.content.decode('utf-8')

# print status
print(len(data), "ads collected")

# write results to a JSON file
with open('results.json', 'w') as f:
    json.dump(data, f)
