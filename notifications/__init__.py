import pkgutil
import importlib
import os

from .base import NotificationBase
from logging_config import logger


def load_notifications():
    """Dynamically load notification modules based on environment variables."""
    enabled_notifications = os.getenv('ENABLED_NOTIFICATIONS', '')  # Example: "email,discord"
    enabled_notifications = [n.strip().lower() for n in enabled_notifications.split(',') if n.strip()]

    notifications = {}

    for finder, name, ispkg in pkgutil.iter_modules(['notifications']):
        if name == 'base':  # Ignore base class
            continue

        if enabled_notifications and name not in enabled_notifications:
            logger.info(f"Skipping disabled notifier: {name}")
            continue

        module = importlib.import_module(f'notifications.{name}')
        
        for attr in dir(module):
            obj = getattr(module, attr)

            if isinstance(obj, type) and issubclass(obj, NotificationBase) and obj != NotificationBase:
                notifications[name] = obj()
                logger.info(f"Loaded notifier: {name}")

    return notifications