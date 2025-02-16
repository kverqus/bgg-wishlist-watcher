import os
import sys

from scrapers import load_scrapers
from wishlist import Wishlist
from database import initialize_db
from utils import update_wishlist
from logging_config import logger
from bot import start_discord_bot


if __name__ == '__main__':
    username = os.getenv('BGG_USERNAME', None)
    run_as_bot = os.getenv('RUN_AS_BOT', None)

    initialize_db()

    scrapers = load_scrapers()

    if run_as_bot:
        if not os.getenv('BOT_TOKEN'):
            logger.warning("Discord bot token not set")
            sys.exit(1)

        logger.info("Starting Discord bot")
        start_discord_bot()

    else:
        if not username:
            logger.info("BGG username not set")
            sys.exit(1)

        wishlist = Wishlist(username=username)
        wishlist.get_wishlist()
        update_wishlist(wishlist)

        for name, scraper in scrapers.items():
            for item in wishlist.items:
                result = scraper.safe_search(item.name)
                print(f"{name}: {result}")
