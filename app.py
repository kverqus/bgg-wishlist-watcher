import pkgutil
import importlib
import os
import sys

from scrapers.base import ScraperBase
from wishlist import Wishlist
from database import initialize_db, add_wishlist_item
from logging_config import logger


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
    username = os.environ['BGG_USERNAME'] if 'BGG_USERNAME' in os.environ else None
    stores = os.environ['SCRAPERS'] if 'SCRAPERS' in os.environ else None
    stores = [store.strip().lower() for store in stores.split(',')] if stores else None

    if not username:
        logger.info("BGG username not set")
        sys.exit(1)

    initialize_db()

    wishlist = Wishlist(username=username)
    wishlist.get_wishlist()
    update_wishlist(wishlist)

    scrapers = load_scrapers()

    for name, scraper in scrapers.items():
        if stores and name.lower() not in stores:
            continue

        for item in wishlist.items:
            result = scraper.safe_search(item.name)
            print(f"{name}: {result}")
