from discord.ext import commands

from database import (
    get_available_scrapers,
    add_scraper_for_user,
    disable_scraper_for_user,
    get_user_scrapers
)


@commands.command()
async def scrapers(ctx):
    """List available scrapers."""
    scrapers_list = get_available_scrapers()
    scrapers_user = get_user_scrapers(ctx.author.id)

    if scrapers_list:
        if scrapers_user:
            await ctx.send(f"Your active scrapers: {', '.join(scrapers_user)}")

        await ctx.send(f"Available scrapers: {', '.join(scrapers_list)}")

    else:
        await ctx.send("No scrapers available.")


@commands.command()
async def add_scraper(ctx, scraper_name: str):
    user_id = ctx.author.id

    scrapers = [s.strip() for s in scraper_name.split(',')]

    if len(scrapers) > 1:
        added_scrapers = []

        for scraper in scrapers:
            status = add_scraper_for_user(user_id, scraper)

            if status:
                added_scrapers.append(scraper)

        if added_scrapers:
            await ctx.send(f"Scrapers '{', '.join(added_scrapers)}' have been enabled for you.")

        else:
            await ctx.send(f"Scrapers '{', '.join(scrapers)}' does not exist or could not be enabled.")

    else:
        if add_scraper_for_user(user_id, scraper_name):
            await ctx.send(f"Scraper '{scraper_name}' has been enabled for you.")

        else:
            await ctx.send(f"Scraper '{scraper_name}' does not exist or could not be enabled.")


@commands.command()
async def remove_scraper(ctx, scraper_name: str):
    user_id = ctx.author.id

    if disable_scraper_for_user(user_id, scraper_name):
        await ctx.send(f"{ctx.author.name}, scraper '{scraper_name}' has been disabled for you.")

    else:
        await ctx.send(f"Scraper '{scraper_name}' is not enabled for you or does not exist.")


async def setup(bot):
    bot.add_command(scrapers)
    bot.add_command(add_scraper)
    bot.add_command(remove_scraper)
