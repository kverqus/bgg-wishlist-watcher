import os
import pkgutil
import importlib
import discord

from discord.ext import commands
from logging_config import logger


def start_discord_bot() -> None:
    """Start the Discord bot."""
    bot_token = os.getenv('BOT_TOKEN', None)

    if not bot_token:
        logger.error("Discord bot token not set")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        # Dynamically load commands
        for finder, name, ispkg in pkgutil.iter_modules(['bot/commands']):
            module_name = f"bot.commands.{name}"

            try:
                await bot.load_extension(module_name)
                logger.info(f"Loaded command module: {module_name}")

            except Exception as e:
                logger.error(f"Failed to load {module_name}: {e}")

        # Dynamically load tasks
        for finder, name, ispkg in pkgutil.iter_modules(['bot/tasks']):
            module_name = f"bot.tasks.{name}"

            try:
                module = importlib.import_module(module_name)

                if hasattr(module, 'setup'):
                    module.setup(bot)
                    logger.info(f"Loaded task module: {module_name}")

            except Exception as e:
                logger.error(f"Failed to load task module {module_name}: {e}")

    bot.run(bot_token)
