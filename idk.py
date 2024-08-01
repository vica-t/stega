import requests
from bs4 import BeautifulSoup

URL = "https://www.ted.com/talks?sort=popular&topics%5B%5D=education"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")