import httpx
import re

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class SFBokScraper(ScraperBase):
    store_name = 'Science Fiction Bokhandeln'

    def _get_item(self, url: str) -> dict:
        url = f"https://www.sfbok.se{url}"
        r = httpx.get(url)
        item = {'price': 0, 'availability': False, 'url': url}

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html5lib')
            price = soup.find('a', attrs={'class': 'add-to-cart'}).text
            price = float(re.search(r'\d+', price).group())
            order_container = soup.find('div', attrs={'class': 'volume-stock'})
            availability = bool(order_container.find(
                'span', attrs={'class': 'glyphicon-ok'}))
            item['price'] = price
            item['availability'] = availability

        return item

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.sfbok.se/search?keys={game_name}&product_type_id=304_305_306_309_310_301_303_312_308_307_318_320_313_321_302_319"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            container = soup.find('div', attrs={'class': 'view-content'})
            items = container.find_all(
                'article', attrs={'class': 'node-teaser'})

        except AttributeError:
            return objects

        for item in items:
            a_container = item.find('h2')
            a = a_container.find('a')
            url = a['href']

            descr = a.text.strip()

            item_ = self._get_item(url)
            item_['name'] = descr

            objects.append(item_)

        objects = find_best_matches(game_name, objects)

        return objects
