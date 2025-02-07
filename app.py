import pkgutil
import importlib

from scrapers.base import ScraperBase
from wishlist import Wishlist


def load_scrapers():
    scrapers = {}
    for finder, name, ispkg in pkgutil.iter_modules(["scrapers"]):
        module = importlib.import_module(f"scrapers.{name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, ScraperBase) and obj != ScraperBase:
                scrapers[name] = obj()
    return scrapers


if __name__ == '__main__':
    scrapers = load_scrapers()
    wishlist = Wishlist(username="Ojeu")
    wishlist.get_wishlist()

    for name, scraper in scrapers.items():
        for item in wishlist.items:
            result = scraper.search(item.name)
            print(f"{name}: {result}")
