import sqlite3
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = "database.db"


def initialize_db():
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

        conn.commit()


def add_wishlist_item(game_name: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO wishlist (name) VALUES (?)", (game_name,))
        conn.commit()
        cursor.execute("SELECT id FROM wishlist WHERE name = ?", (game_name,))
        return cursor.fetchone()[0]


def get_store_id(store_name: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM store WHERE NAME = ?", (store_name,))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute("INSERT INTO store (name) VALUES (?)", (store_name,))
        conn.commit()

        return cursor.lastrowid


def get_game_id(store_id, game_name, url):
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


def insert_price(game_id, price, availability):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO price (game_id, price, availability) VALUES (?, ?, ?)",
                       (game_id, price, availability))
        conn.commit()


def link_wishlist_game(wishlist_id, game_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO wishlist_game (wishlist_id, game_id) VALUES (?, ?)", (wishlist_id, game_id))
        conn.commit()


def is_price_lower(wishlist_id, new_price, availability):
    """Check if the new price is lower than any previous price for all versions of a game in the wishlist."""
    if availability != 1:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT game_id FROM wishlist_game WHERE wishlist_id = ?",
            (wishlist_id,),
        )
        game_ids = [row[0] for row in cursor.fetchall()]

        if not game_ids:
            return False

        # Get the lowest in-stock price among all linked games
        cursor.execute(
            f"""
            SELECT MIN(price) FROM price
            WHERE game_id IN ({','.join('?' * len(game_ids))})
            AND availability = 1
            """,
            game_ids
        )
        result = cursor.fetchone()

        if result and result[0] is not None:
            lowest_price = float(result[0])
            return float(new_price) < lowest_price

        return False


def save_game_result(wishlist_name, store_name, game_name, price, availability, url):
    wishlist_id = add_wishlist_item(wishlist_name)
    store_id = get_store_id(store_name)
    game_id = get_game_id(store_id, game_name, url)

    insert_price(game_id, price, availability)  # Store price history
    link_wishlist_game(wishlist_id, game_id)  # Link wishlist and game
