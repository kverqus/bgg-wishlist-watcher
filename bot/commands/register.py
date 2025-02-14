from discord.ext import commands

from database import register_user


@commands.command()
async def register(ctx, bgg_username: str):
    """Register a user with their BGG username."""
    success = register_user(str(ctx.author.id), bgg_username)
    if success:
        await ctx.send(f"✅ Registered {ctx.author.name} with BGG username: {bgg_username}")
    else:
        await ctx.send(f"⚠️ You are already registered!")


async def setup(bot):
    bot.add_command(register)