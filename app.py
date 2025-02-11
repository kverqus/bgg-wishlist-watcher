import os
import sys

from scrapers import load_scrapers
from wishlist import Wishlist
from database import initialize_db, add_wishlist_item
from logging_config import logger


def update_wishlist(wishlist: Wishlist):
    for item in wishlist.items:
        add_wishlist_item(item.name)


if __name__ == '__main__':
    username = os.getenv('BGG_USERNAME', None)

    if not username:
        logger.info("BGG username not set")
        sys.exit(1)

    initialize_db()

    wishlist = Wishlist(username=username)
    wishlist.get_wishlist()
    update_wishlist(wishlist)

    scrapers = load_scrapers()

    for name, scraper in scrapers.items():
        for item in wishlist.items:
            result = scraper.safe_search(item.name)
            print(f"{name}: {result}")
