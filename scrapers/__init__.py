import pkgutil
import importlib

from typing import Union
from .base import ScraperBase
from logging_config import logger


def load_scrapers(scrapers_to_load: Union[str, None]) -> dict:
    scrapers = {}

    for finder, name, ispkg in pkgutil.iter_modules(["scrapers"]):
        if scrapers_to_load and name.lower() not in scrapers_to_load:
            continue

        module = importlib.import_module(f"scrapers.{name}")

        for attr in dir(module):
            obj = getattr(module, attr)

            if isinstance(obj, type) and issubclass(obj, ScraperBase) and obj != ScraperBase:
                scrapers[name] = obj()
                logger.info(f"Loaded scraper: {name}")

    return scrapers