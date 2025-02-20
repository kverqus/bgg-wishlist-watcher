import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class SpelexpertenScraper(ScraperBase):
    store_name = 'Spelexperten'

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.spelexperten.com/cgi-bin/ibutik/AIR_ibutik.fcgi?funk=gor_sokning&AvanceradSokning=N&artnr=&varum=&artgrp=&Sprak_Suffix=SV&term={game_name}"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            container = soup.find(
                'div', attrs={'class': 'search-articles-wrapper'})
            items = container.find_all('div', attrs={'class': 'PT_Wrapper'})

        except AttributeError:
            return objects

        for item in items:
            a = item.find('a')
            url = a['href']
            descr = a['aria-label']
            price = item.find('span', attrs={'class': 'PT_PrisNormal'})
            price = float(price.text.split()[0])
            availability = bool(
                item.find('div', attrs={'class': 'buy-button'}))

            objects.append({
                'name': descr,
                'price': price,
                'availability': availability,
                'url': f"https://www.spelexperten.com{url}"
            })

        objects = find_best_matches(game_name, objects)

        return objects
