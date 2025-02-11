from abc import ABC, abstractmethod

from logging_config import logger


class NotificationBase(ABC):
    @abstractmethod
    def send(self, title, message):
        """Send a notification with the given title and message."""
        pass

    def safe_send(self, title, message):
        """Wrapper to log execution and handle errors."""
        try:
            logger.info(f"Sending notification: {title} - {message}")
            self.send(title, message)
            logger.info("Notification sent successfully")

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")