import httpx

from bs4 import BeautifulSoup

from utils import find_best_matches
from scrapers.base import ScraperBase


class WorldOfBoardgamesScraper(ScraperBase):
    store_name = 'WorldofBoardGames'

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.worldofboardgames.com/sok/{game_name}"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            items = soup.find_all('li', attrs={'class': 'productContainer'})

        except AttributeError:
            return objects

        for item in items:
            a = item.find('a')
            url = a['href']
            descr = a['title']
            price = float(item.find('strong').text.split()[0])
            availability = item.find('a', attrs={'class': 'button'})
            availability = True if 'green' in availability.get('class') else False

            objects.append({
                'name': descr,
                'price': price,
                'availability': availability,
                'url': url
            })

        objects = find_best_matches(game_name, objects)

        return objects
