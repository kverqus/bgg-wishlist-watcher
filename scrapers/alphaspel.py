import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class AlphaspelScraper(ScraperBase):
    def _get_item(self, url: str) -> dict:
        url = f"https://alphaspel.se{url}"
        r = httpx.get(url)
        item = {'price': 0, 'in_stock': False, 'url': url}

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html5lib')
            price = soup.find('div', attrs={'class': 'price'})
            price = int(price.text.split()[0])
            order_container = soup.find(
                'form', attrs={'class': 'main-product-add-to-cart'})
            in_stock = bool(order_container.find(
                'a', attrs={'class': 'btn-success'}))
            item['price'] = price
            item['in_stock'] = in_stock

        return item

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://alphaspel.se/search/?query={game_name}"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            container = soup.find('div', attrs={'class': 'products'})
            items = container.find_all('div', attrs={'class': 'product'})

        except AttributeError:
            return objects

        for item in items:
            a = item.find('a')['href']

            if not a:
                pass

            item_ = self._get_item(a)
            item_['name'] = item.find('div', attrs={'class': 'product-name'}).text.strip()

            objects.append(item_)

        objects = find_best_matches(game_name, objects)

        return objects
