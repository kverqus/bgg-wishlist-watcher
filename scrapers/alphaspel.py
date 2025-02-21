import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class AlphaspelScraper(ScraperBase):
    store_name = 'Alphaspel'

    async def search(self, game_name: str) -> list:
        objects = []
        url = f"https://alphaspel.se/search/?query={game_name}"

        async with httpx.AsyncClient() as client:
            r = await client.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            container = soup.find('div', attrs={'class': 'products'})
            items = container.find_all('div', attrs={'class': 'product'})

        except AttributeError:
            return objects

        for item in items:
            url = item.find('a')['href']
            price = float(item.find('div', attrs={'class': 'price'}).text.strip().split()[0])
            availability = item.find('a', attrs={'class': 'add-to-cart'})
            availability = bool('btn-success' in availability.get('class'))
            descr = item.find('div', attrs={'class': 'product-name'})

            for hidden in descr.find_all('small'):
                hidden.extract()

            objects.append({
                'name': descr.text.strip(),
                'price': price,
                'availability': availability,
                'url': f"https://alphaspel.se{url}"
            })

        objects = find_best_matches(game_name, objects)

        return objects
