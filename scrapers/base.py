from abc import ABC, abstractmethod

from database import save_game_result
from logging_config import logger


class ScraperBase(ABC):
    store_name = None

    @abstractmethod
    async def search(self, game_name: str) -> None:
        """Search for the board game and return price and availability."""
        pass

    async def safe_search(self, wishlist_name: str, commit: bool = True) -> list:
        """Wrapper to log execution, handle errors, and save results."""
        try:
            logger.info(f"Searching for game: {wishlist_name}")
            result = await self.search(wishlist_name)
            logger.info(f"Search successful: {result}")

            if result and commit:
                for item in result:
                    save_game_result(wishlist_name, self.store_name,
                                    item['name'], item['price'], item['availability'], item['url'])

            return result

        except Exception as e:
            logger.error(f"Error searching for {wishlist_name}: {e}")
            return {"error": "Failed to retrieve game data"}
