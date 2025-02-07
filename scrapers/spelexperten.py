import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class SpelexpertenScraper(ScraperBase):
    def _get_item(self, url: str) -> dict:
        url = f"https://www.spelexperten.com{url}"
        r = httpx.get(url)
        item = {'price': 0, 'in_stock': False, 'url': url}

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html5lib')
            price = soup.find('span', attrs={'class': 'PrisBOLD'})
            price = int(price.text.split(' ')[0])
            order_container = soup.find('div', attrs={'id': 'OrderFalt'})
            in_stock = bool(order_container.find(
                'div', attrs={'class': 'buy-button'}))
            item['price'] = price
            item['in_stock'] = in_stock

        return item

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.spelexperten.com/cgi-bin/ibutik/API.fcgi?funk=as_fil&chars={game_name}&retur=html&Sprak_Suffix=SV"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            container = soup.find('ul', attrs={'class': 'LSS_Artiklar'})
            items = container.find_all('li')

        except AttributeError:
            return objects

        for item in items:
            a = item.find('a')['href']

            if not a:
                pass

            descr = item.find('span', attrs={'class': 'Beskr'})

            for hidden in descr.find_all('span', attrs={'class': 'LSS_META'}):
                hidden.extract()

            descr = descr.text.strip()
            item_ = self._get_item(a)
            item_['name'] = descr

            objects.append(item_)

        objects = find_best_matches(game_name, objects)

        return objects
