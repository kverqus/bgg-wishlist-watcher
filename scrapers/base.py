from abc import ABC, abstractmethod


class ScraperBase(ABC):
    @abstractmethod
    def search(self, game_name: str) -> None:
        """Search for the board game and return price and availability."""
        pass