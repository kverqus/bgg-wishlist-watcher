import os
import sys

from scrapers import load_scrapers
from database import initialize_db
from logging_config import logger
from bot import start_discord_bot


if __name__ == '__main__':
    initialize_db()

    scrapers = load_scrapers()

    if not os.getenv('BOT_TOKEN'):
        logger.warning("Discord bot token not set")
        sys.exit(1)

    logger.info("Starting Discord bot")
    start_discord_bot()

