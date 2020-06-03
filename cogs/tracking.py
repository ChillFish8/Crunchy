import re
import discord
import asyncio

from discord.ext import commands

from database.database import UserFavourites, UserRecommended, UserWatchlist

async def add_watchlist(ctx, name, url):
    pass

async def add_favourites(ctx, name, url):
    pass

async def add_both(*args, **kwargs):
    return (await add_favourites(*args, **kwargs)), (await add_watchlist(*args, **kwargs))

class TrackingAnime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_re = re.compile("""url=(["'])(?:(?=(\\?))\2.)*?\1""")
        self.options = {0: add_favourites, 1: add_watchlist, 2: add_both}

    @commands.command(aliases=['aa', 'addanime'])
    async def add_anime(self, ctx, *, argument: str):
        """ Add Anime to a collection """
        items = argument.split("url=", 1)
        if len(items) > 1:
            name, url = items
            if name == '':
                split = url.split(" ", 1)
                if len(split) > 1:  # Reverse the order in case someone is a moron
                    name, url = split[1], split[0]
                else:
                    return await ctx.send(f"<:HimeMad:676087826827444227> Oops! "
                                          f"You didnt give a title but gave a url, "
                                          f"please do `{ctx.prefix}help addanime` for more info.")
            if not url.startswith("http"):
                url = None
        else:
            name, url = items[0], None
        if name.endswith(" "):
            name = name[:len(name) - 1]

        desc = f"Where would you like the Anime to go?\n" \
               f"Click on the Emoji related to the choice you want to make!\n\n" \
               f"💖 **- Add to Favourites**\n\n" \
               f"<:CrunchyRollLogo:676087821596885013> **- Add to watchlist**\n\n" \
               f"<:9887_ServerOwner:653722257356750889> **- Add to both lists**\n\n"

        embed = discord.Embed(
            title="What list should I add it to?",
            description=desc,
            color=self.bot.colour
        )

        message: discord.Message = await ctx.send(embed=embed)
        BASE_EMOJIS = [
            "💖", "<:CrunchyRollLogo:676087821596885013>", "<:9887_ServerOwner:653722257356750889>"
        ]
        for emoji in BASE_EMOJIS:
            await message.add_reaction(emoji)

        def check(r: discord.Reaction, u: discord.User):
            return (str(r.emoji) in BASE_EMOJIS) and (u.id == ctx.author.id) and (r.message.id == message.id)

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return await message.edit(content="The selection period has expired.")

        results = await self.options[BASE_EMOJIS.index(str(reaction.emoji))](ctx, name, url)
        if len(results) < 2:
            if not results:
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to your list!")
            else:
                return await ctx.send(**results)
        else:
            if not results[0] or not results[1]:
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to your list!")
            else:
                return await ctx.send(f"<:HimeHappy:677852789074034691> Success!"
                                      f" I've added {name} to both your watchlist and favourites!")


def setup(bot):
    bot.add_cog(TrackingAnime(bot))
