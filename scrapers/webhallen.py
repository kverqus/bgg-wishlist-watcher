import httpx
import json

from utils import find_best_matches
from scrapers.base import ScraperBase


class WebhallenScraper(ScraperBase):
    store_name = 'Webhallen'

    def search(self, game_name: str) -> list:
        objects = []
        url = f"https://www.webhallen.com/api/productdiscovery/search/{game_name}?page=1&touchpoint=DESKTOP&totalProductCountSet=false&origin=ORGANIC"
        r = httpx.get(url)

        if r.status_code != 200:
            return objects

        response = json.loads(r.content)

        for product in response['products']:
            objects.append({
                'price': float(product['price']['price']),
                'availability': True if product['stock']['web'] > 0 else False,
                'url': f"https://www.webhallen.com/se/product/{product['id']}",
                'name': product['name']
            })

        objects = find_best_matches(game_name, objects)

        return objects
