import sqlite3

from logging_config import logger
from wishlist import Wishlist

from typing import Union


DB_NAME = "database.db"


def initialize_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                game_name TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                price REAL NOT NULL,
                availability INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist_game (
                wishlist_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                PRIMARY KEY (wishlist_id, game_id),
                FOREIGN KEY (wishlist_id) REFERENCES wishlist(id) ON DELETE CASCADE,
                FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraper (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Tables used by Discord bot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                bgg_username TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_wishlist (
                user_id INTEGER NOT NULL,
                wishlist_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, wishlist_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (wishlist_id) REFERENCES wishlist(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scraper (
                user_id INTEGER NOT NULL,
                scraper_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, scraper_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (scraper_id) REFERENCES scraper(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()


def add_wishlist_item(game_name: str) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO wishlist (name) VALUES (?)", (game_name,))
        conn.commit()
        cursor.execute("SELECT id FROM wishlist WHERE name = ?", (game_name,))
        return cursor.fetchone()[0]


def get_store_id(store_name: str) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM store WHERE NAME = ?", (store_name,))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute("INSERT INTO store (name) VALUES (?)", (store_name,))
        conn.commit()

        return cursor.lastrowid


def get_game_id(store_id: int, game_name: str, url: str) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM game WHERE store_id = ? AND url = ?", (store_id, url))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute(
            "INSERT INTO game (store_id, game_name, url) VALUES (?, ?, ?)", (store_id, game_name, url))
        conn.commit()
        return cursor.lastrowid


def insert_price(game_id: int, price: float, availability: bool) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO price (game_id, price, availability) VALUES (?, ?, ?)",
                       (game_id, price, availability))
        conn.commit()


def link_wishlist_game(wishlist_id: int, game_id: int) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO wishlist_game (wishlist_id, game_id) VALUES (?, ?)", (wishlist_id, game_id))
        conn.commit()


def is_price_lower(game_id: int, new_price: float, availability: bool) -> bool:
    """Check if the new price is lower than the previously recorded price for the same version of the game"""

    if availability != 1:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT price FROM price
            WHERE game_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (game_id,),
        )

        result = cursor.fetchone()

        if result and result[0] is not None:
            previous_price = result[0]
            return new_price < previous_price

        return False


def is_back_in_stock(game_id: int, availability: bool) -> bool:
    """Check if game is back in stock"""

    if availability != 1:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT availability FROM price
            WHERE game_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (game_id,),
        )

        result = cursor.fetchone()

    if result and not result[0]:
        return True

    return False


def save_game_result(wishlist_name: str, store_name: str, game_name: str, price: float, availability: bool, url: str):
    """Save game results, track price changes, log price drops and items back in stock"""

    wishlist_id = add_wishlist_item(wishlist_name)
    store_id = get_store_id(store_name)
    game_id = get_game_id(store_id, game_name, url)

    if is_price_lower(game_id, price, availability):
        logger.info(
            f"Price drop detected: {game_name} is now {price} at {store_name} ({url})")

    if is_back_in_stock(game_id, availability):
        logger.info(
            f"Back in stock: {game_name} is now back in stock at {store_name} ({url})")

    insert_price(game_id, price, availability)  # Store price history
    link_wishlist_game(wishlist_id, game_id)  # Link wishlist and game


# Functions used by Discord bot


def add_scraper_to_db(scraper_name: str) -> None:
    """Ensure the scraper exists in the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO scraper (name) VALUES (?)", (scraper_name,))
            conn.commit()

            logger.info(f"Scraper '{scraper_name}' added to database.")

        except sqlite3.DatabaseError as e:
            logger.error(
                f"Failed to insert scraper '{scraper_name}' into database: {e}")


def remove_obsolete_scrapers(active_scrapers: set) -> None:
    """Remove scrapers from the database that are no longer available."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM scraper")
        db_scrapers = {row[0] for row in cursor.fetchall()}

        obsolete_scrapers = db_scrapers - active_scrapers

        if obsolete_scrapers:
            cursor.executemany("DELETE FROM scraper WHERE name = ?", [
                               (name,) for name in obsolete_scrapers])
            conn.commit()

            logger.info(
                f"Removed obsolete scrapers from database: {', '.join(obsolete_scrapers)}")


def register_user(discord_id: str, bgg_username: str) -> bool:
    """Register a Discord user with their BGG username."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO user (discord_id, bgg_username) VALUES (?, ?)", (discord_id, bgg_username))
            conn.commit()

            return True

        except sqlite3.IntegrityError:
            return False


def get_all_users() -> Union[list, None]:
    """Fetch all registered users."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT discord_id FROM user")

        result = cursor.fetchall()

    return [row[0] for row in result] if result else None


def get_user_bgg_username(discord_id: str) -> str:
    """Fetch the BGG username for a given Discord user ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT bgg_username FROM user WHERE discord_id = ?", (discord_id,))

        result = cursor.fetchone()

        return result[0] if result else None


def add_wishlist_to_user(discord_id: str) -> Union[list, None]:
    """Fetch wishlist from BGG and link it to the user."""
    bgg_username = get_user_bgg_username(discord_id)

    if not bgg_username:
        return None  # User not registered

    wishlist = Wishlist(username=bgg_username)
    wishlist.get_wishlist()
    wishlist_games = wishlist.items

    if not wishlist_games:
        return []

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        for game in wishlist_games:
            cursor.execute(
                "INSERT OR IGNORE INTO wishlist (name) VALUES (?)", (game.name,))
            cursor.execute(
                "SELECT id FROM wishlist WHERE name = ?", (game.name,))

            wishlist_id = cursor.fetchone()[0]

            # Link item to user
            cursor.execute(
                "INSERT OR IGNORE INTO user_wishlist (user_id, wishlist_id) VALUES ((SELECT id FROM user WHERE discord_id = ?), ?)", (discord_id, wishlist_id))

        conn.commit()

    return wishlist_games


def get_available_scrapers() -> list[str]:
    """Retrieve a list of all available scrapers from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM scraper")

        return [row[0] for row in cursor.fetchall()]


def add_scraper_for_user(discord_id: str, scraper_name: str) -> bool:
    """Add a scraper to the user's configured scrapers."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO user_scraper (user_id, scraper_id)
                VALUES ((SELECT id FROM user WHERE discord_id = ?), (SELECT id FROM scraper WHERE name = ?))
            """, (discord_id, scraper_name))
            conn.commit()

            return True

        except sqlite3.IntegrityError:
            return False  # Scraper already exists for this user


def disable_scraper_for_user(discord_id: int, scraper_name: str) -> bool:
    """Disable a specific scraper for a user."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM scraper WHERE name = ?",
                       (scraper_name,))
        scraper = cursor.fetchone()

        if not scraper:
            return False

        scraper_id = scraper[0]

        # Remove the user's association with this scraper
        cursor.execute(
            "DELETE FROM user_scraper WHERE user_id = (SELECT id FROM user WHERE discord_id = ?) AND scraper_id = ?", (discord_id, scraper_id))
        conn.commit()
        return True


def get_user_scrapers(discord_id: str) -> list[str]:
    """Retrieve a list of scrapers configured for the user."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.name FROM scraper s
            JOIN user_scraper us ON s.id = us.scraper_id
            WHERE us.user_id = (SELECT id FROM user WHERE discord_id = ?)
        """, (discord_id,))

        return [row[0] for row in cursor.fetchall()]
