import pkgutil
import importlib
import os

from .base import ScraperBase
from logging_config import logger
from database import add_scraper_to_db, remove_obsolete_scrapers


def load_scrapers() -> dict:
    enabled_scrapers = os.getenv('SCRAPERS', None)
    enabled_scrapers = [store.strip().lower() for store in enabled_scrapers.split(',')] if enabled_scrapers else None
    scrapers = {}
    active_scrapers = set()

    for finder, name, ispkg in pkgutil.iter_modules(['scrapers']):
        if name == 'base':  # Ignore base class
            continue

        if enabled_scrapers and name.lower() not in enabled_scrapers:
            continue

        module = importlib.import_module(f'scrapers.{name}')

        for attr in dir(module):
            obj = getattr(module, attr)

            if isinstance(obj, type) and issubclass(obj, ScraperBase) and obj != ScraperBase:
                scrapers[name] = obj()
                active_scrapers.add(name)

                logger.info(f"Loaded scraper: {name}")

                add_scraper_to_db(name)

    remove_obsolete_scrapers(active_scrapers)

    return scrapers