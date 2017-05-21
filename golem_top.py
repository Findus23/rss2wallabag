from bs4 import BeautifulSoup

import requests


def get_top_articles():
    r = requests.get("https://www.golem.de/")
    s = BeautifulSoup(r.text, "html.parser")

    return [a["href"] for a in s.find(id=["recent-articles"]).find_all("a")[:2]]
