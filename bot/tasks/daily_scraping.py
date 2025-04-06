import asyncio
import discord
import aiocron
from database import (
    get_wishlist_games
)
from scrapers import load_scrapers

from logging_config import logger


async def scrape_games(scraper):
    """Scrape all wishlist games and store results in the database."""
    wishlist_games = get_wishlist_games()
    results = []

    if not wishlist_games:
        logger.info(f"No games found in wishlist for {scraper.store_name}.")
        return

    logger.info(f"Scraping {len(wishlist_games)} games from {scraper.store_name}.")

    for game in wishlist_games:
        result = await scraper.safe_search(game)
        if result:
            results.append(result)

    # Filter out empty results
    items = [result for result in results if result]

    logger.info(f"Scraping {scraper.store_name} complete. {len(items)} results stored.")

async def scrape_all_games(bot: discord.ext.commands.Bot):
    """Schedule all scrapers as separate background tasks to avoid blocking."""
    scrapers = load_scrapers()

    if not scrapers:
        logger.error("No scrapers loaded.")
        return

    logger.info(f"Starting {len(scrapers)} scraper tasks in background.")

    for scraper in scrapers.values():
        asyncio.create_task(scrape_games(scraper))  # Non-blocking

def setup(bot: discord.ext.commands.Bot):
    """Schedule the scraping task in the background at 05:30 UTC."""
    aiocron.crontab('30 9 * * *', func=lambda: asyncio.create_task(scrape_all_games(bot)))
    logger.info("Scheduled scraping task.")