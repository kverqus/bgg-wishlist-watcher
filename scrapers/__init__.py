import pkgutil
import importlib
import os

from .base import ScraperBase
from logging_config import logger


def load_scrapers() -> dict:
    STORES = os.getenv('SCRAPERS', None)
    STORES = [store.strip().lower() for store in STORES.split(',')] if STORES else None
    scrapers = {}

    for finder, name, ispkg in pkgutil.iter_modules(["scrapers"]):
        if STORES and name.lower() not in STORES:
            continue

        module = importlib.import_module(f"scrapers.{name}")

        for attr in dir(module):
            obj = getattr(module, attr)

            if isinstance(obj, type) and issubclass(obj, ScraperBase) and obj != ScraperBase:
                scrapers[name] = obj()
                logger.info(f"Loaded scraper: {name}")

    return scrapers