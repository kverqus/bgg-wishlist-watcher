from time import sleep
from typing import Union

import xml.etree.ElementTree as ET
import httpx


class Wishlist:
    def __init__(self, username: str):
        self.url = f'https://boardgamegeek.com/xmlapi/collection/{username}?wishlist=1'
        self.items = []

    def __parse_wishlist(self, wishlist: 'xml.etree.ElementTree.Element') -> Union[str, list]:
        root = ET.fromstring(wishlist)

        match root.tag:
            case 'message':
                print("Wishlist not generated")
                sleep(1)
                return self.__parse_wishlist(wishlist)

            case 'errors':
                errors = root.findall('error')
                return ', '.join([error.find('message').text for error in errors])

        for item_ in root:
            item = WishlistItem(
                name=item_.find('name').text,
                url=f"https://boardgamegeek.com/boardgame/{item_.get('objectid')}"
            )
            self.items.append(item)

        return self.items

    def get_wishlist(self) -> bool:
        r = httpx.get(self.url)

        if r.status_code == 200:
            self.__parse_wishlist(r.content)

        if len(self.items) > 0:
            return True

        return False


class WishlistItem:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.price = 0
        self.store_url = None

    def __repr__(self):
        return f"<WishlistItem {self.name}>"
