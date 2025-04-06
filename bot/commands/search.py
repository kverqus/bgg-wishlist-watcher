from itertools import chain
from discord.ext import commands
from scrapers import load_scrapers


@commands.command()
async def search(ctx, game_name: str):
    scrapers = load_scrapers()
    results = []

    await ctx.send(f"Finding the best price for '{game_name}'")

    for name, scraper in scrapers.items():
        result = await scraper.safe_search(game_name, commit=False)
        if result:
            results.append(result)

    if not result:
        await ctx.send(f"No results found for query '{game_name}'")
        return

    flat_result = list(chain.from_iterable(results))
    sorted_result = sorted(
        (item for item in flat_result if isinstance(item, dict) and 'price' in item),
        key=lambda x: x['price'])
    filtered_result = [
        item for item in sorted_result if item.get('availability', False)]

    if not filtered_result:
        await ctx.send(f"Game '{game_name}' found in {len(sorted_result)} {'store' if len(sorted_result) == 1 else 'stores'}, but is not in stock")
        return
    
    max_items = filtered_result[:5]
    out_of = f"Displaying {len(max_items)} out of {len(filtered_result)} results for query '{game_name}'" if max_items < filtered_result else f"Displaying {len(max_items)} results for query '{game_name}'"
    items = '\n'.join([f"**[{r['name']}](<{r['url']}>)** for {r['price']} SEK" for r in max_items])

    await ctx.send(f"{out_of}\n{items}")


async def setup(bot):
    bot.add_command(search)
