from discord.ext import commands

from database import add_wishlist_to_user


@commands.command()
async def wishlist(ctx):
    """Fetch and save wishlist for the registered user."""
    games = add_wishlist_to_user(str(ctx.author.id))

    if games is None:
        await ctx.send("⚠️ You are not registered. Use `!register <BGG username>` first.")

    elif not games:
        await ctx.send("❌ No wishlist found on BGG.")

    else:
        await ctx.send(f"✅ Your wishlist has been updated with {len(games)} games!")


async def setup(bot):
    bot.add_command(wishlist)