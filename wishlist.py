import xml.etree.ElementTree as ET
import httpx

from time import sleep

from logging_config import logger


class Wishlist:
    def __init__(self, username: str):
        self.username = username
        self.url = f'https://boardgamegeek.com/xmlapi/collection/{username}?wishlist=1'
        self.items = []

    def __parse_wishlist(self, wishlist: 'ET.Element') -> list:
        root = ET.fromstring(wishlist)

        if 'errors' in root.tag:
            errors = root.findall('error')
            errors = ', '.join(
                [error.find('message').text for error in errors])

            logger.warning(f"Errors while parsing wishlist: {errors}")

            return self.items

        for item_ in root:
            item = WishlistItem(
                name=item_.find('name').text,
                url=f"https://boardgamegeek.com/boardgame/{item_.get('objectid')}"
            )
            self.items.append(item)

        return self.items

    def get_wishlist(self) -> None:
        r = httpx.get(self.url)

        if r.status_code == 202:
            logger.info("Request has been queued by the BGG API")
            sleep(1)
            return self.get_wishlist()

        if r.status_code != 200:
            logger.warning(
                f"Unable to fetch wishlist. Status code returned: {r.status_code}")
            return

        self.__parse_wishlist(r.content)

        if len(self.items) == 0:
            logger.info("Wishlist is empty")
            return

        logger.info(
            f"{len(self.items)} items gathered from wishlist for {self.username}")


class WishlistItem:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.price = 0
        self.store_url = None

    def __repr__(self) -> str:
        return f"<WishlistItem {self.name}>"
