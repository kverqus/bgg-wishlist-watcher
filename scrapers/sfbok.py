import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class SFBokScraper(ScraperBase):
    store_name = 'Science Fiction Bokhandeln'

    async def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.sfbok.se/search?keys={game_name}&product_type_id=304_305_306_309_310_301_303_312_308_307_318_320_313_321_302_319"

        async with httpx.AsyncClient() as client:
            r = await client.get(url)

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
            a = item.find('h2')
            url = a.find('a')['href']
            descr = a.find('a').text.strip()
            price = float(item.find('div', attrs={'class': 'price'}).text.split()[0])
            availability = bool(item.find('li', attrs={'class': 'cart'}))

            objects.append({
                'name': descr,
                'price': price,
                'availability': availability,
                'url': f"https://www.sfbok.se{url}"
            })

        objects = find_best_matches(game_name, objects)

        return objects
