import pkgutil
import importlib

from scrapers.base import ScraperBase
from wishlist import Wishlist
from database import initialize_db, add_wishlist_item


def load_scrapers() -> dict:
    scrapers = {}
    for finder, name, ispkg in pkgutil.iter_modules(["scrapers"]):
        module = importlib.import_module(f"scrapers.{name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, ScraperBase) and obj != ScraperBase:
                scrapers[name] = obj()
    return scrapers


def update_wishlist(wishlist: Wishlist):
    for item in wishlist.items:
        add_wishlist_item(item.name)


if __name__ == '__main__':
    initialize_db()
    scrapers = load_scrapers()
    wishlist = Wishlist(username="Ojeu")
    wishlist.get_wishlist()

    update_wishlist(wishlist)

    for name, scraper in scrapers.items():
        for item in wishlist.items:
            result = scraper.safe_search(item.name)
            print(f"{name}: {result}")
