import aiocron
import discord
import asyncio

from logging_config import logger
from database import get_all_users, get_user_bgg_username, get_user_wishlist_games, get_previous_prices, add_wishlist_to_user

from datetime import datetime, timedelta


async def process_user(bot: discord.ext.commands.Bot, discord_id: int):
    """Process a single user, fetching wishlist from bgg."""
    user = bot.get_user(int(discord_id))
    if not user:
        return

    try:
        bgg_username = get_user_bgg_username(discord_id)

        if not bgg_username:
            logger.info(f"No BGG username set for {user}")
            return

        add_wishlist_to_user(discord_id)

    except Exception as e:
        logger.error(f"Error processing {user} wishlist: {e}")


async def update_wishlists(bot: discord.ext.commands.Bot):
    """Fetch all registered users and process them asynchronously."""
    try:
        users = get_all_users()

        if not users:
            logger.info("No registered users to process")
            return

        tasks = [process_user(bot, discord_id) for discord_id in users]
        await asyncio.gather(*tasks)  # Run all users in parallel

    except Exception as e:
        logger.error(f"Error in update_wishlists: {e}")


async def process_wishlist(bot: discord.ext.commands.Bot, discord_id: int):
    """Process user wishlist and notify user on changes"""
    def __remove_empty_entries(d):
        if isinstance(d, dict):
            return {k: __remove_empty_entries(v) for k, v in d.items() if __remove_empty_entries(v) != {} and __remove_empty_entries(v) != []}
        return d

    notifications = []
    notification = ''
    result = {'back_in_stock': {}, 'lower_price': {}, 'new': {}}

    try:
        user = await bot.fetch_user(discord_id)

        if not user:
            logger.error(f"User not found while executing process_wishlist")
            raise

        wishlist_items = get_user_wishlist_games(discord_id)

        for item in wishlist_items:
            game = {
                'wishlist_name': item[1],
                'game_id': item[2],
                'scraped_name': item[3],
                'store_url': item[4],
                'store_id': item[5],
                'store_name': item[6],
                'prices': {
                    'old': {},
                    'current': {}
                }
            }

            for i in ['back_in_stock', 'lower_price', 'new']:
                if not game['wishlist_name'] in result[i]:
                    result[i][game['wishlist_name']] = []

            previous_prices = get_previous_prices(game['scraped_name'], game['store_id'])
            game['prices']['current']['price'] = previous_prices[0][0]
            game['prices']['current']['availability'] = previous_prices[0][1]
            game['prices']['current']['timestamp'] = previous_prices[0][2]
            game['prices']['old']['price'] = previous_prices[1][0] if len(previous_prices) > 1 else None
            game['prices']['old']['availability'] = previous_prices[1][1] if len(previous_prices) > 1 else False
            game['prices']['old']['timestamp'] = previous_prices[1][2] if len(previous_prices) > 1 else None

            timestamp = datetime.strptime(game['prices']['current']['timestamp'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()

            if timestamp >= now - timedelta(days=2):
                pass

            if not game['prices']['old']['price'] and game['prices']['current']['availability']:
                result['new'][game['wishlist_name']].append(game)

            elif game['prices']['current']['availability'] and game['prices']['current']['price'] < game['prices']['old']['price']:
                result['lower_price'][game['wishlist_name']].append(game)

            elif game['prices']['current']['availability'] > game['prices']['old']['availability']:
                result['back_in_stock'][game['wishlist_name']].append(game)

        result = __remove_empty_entries(result)

        if not result:
            logger.info(f"No updates for {user}")
            return

        for key in result.keys():
            for game in result[key]:
                result[key][game] = min(result[key][game], key=lambda x: x['prices']['current']['price'])

        for key in result.keys():
            if key == 'new':
                notification += "\n## Newly discovered"

            if key == 'lower_price':
                notification += "\n## Lowered price"

            if key == 'back_in_stock':
                notification += "\n## Back in stock"

            for k in result[key]:
                game = result[key][k]
                message = f"\n**{game['scraped_name']}**: [{game['store_name']}](<{game['store_url']}>) for {game['prices']['current']['price']} SEK\n-# Updated at {game['prices']['current']['timestamp']}"

                if len(message) + len(notification) >= 2000:
                    notifications.append(notification)
                    notification = message
                else:
                    notification += message

            notifications.append(notification)

        for notification in notifications:
            await user.send(notification)

    except Exception as e:
        logger.error(f"Error in process_wishlist: {e}")
    

async def notify_user(bot: discord.ext.commands.Bot):
    """Create tasks for wishlist processing"""
    try:
        users = get_all_users()
        tasks = [process_wishlist(bot, discord_id) for discord_id in users]            
        await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Error in notify_user: {e}")


def setup(bot: discord.ext.commands.Bot):
    aiocron.crontab('30 5 * * *')(lambda: bot.loop.create_task(update_wishlists(bot)))
    aiocron.crontab('30 10 * * *')(lambda: bot.loop.create_task(notify_user(bot)))
    logger.info("Scheduled daily user wishlist update.")