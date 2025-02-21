import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class SpelOchSantScraper(ScraperBase):
    store_name = 'Spel & Sånt'

    async def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.spelochsant.se/products/search?query={game_name}&manufacturers=&search_sorting=search_rank&search_sorting_direction=desc"

        async with httpx.AsyncClient() as client:
            r = await client.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            items = soup.find_all('div', attrs={'class': 'product'})

        except AttributeError:
            return objects

        for item in items:
            a = item.find('div', attrs={'sl-information__title'})
            url = a.find('a')['href']
            price = float(item.find('div', attrs={'class': 'sl-price-big'}).text.strip().split()[0])
            availability = item.find('div', attrs={'class': 'stock_bomb'})
            availability = bool(availability.find('div', attrs={'class': 'green_bomb'}))
            descr = a.find('a').text.strip()

            objects.append({
                'name': descr,
                'price': price,
                'availability': availability,
                'url': f"https://www.spelochsant.se{url}"
            })

        objects = find_best_matches(game_name, objects)

        return objects
