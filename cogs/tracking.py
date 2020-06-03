import re
import discord

from discord.ext import commands

from database.database import UserFavourites, UserRecommended, UserWatchlist


class TrackingAnime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_re = re.compile("""url=(["'])(?:(?=(\\?))\2.)*?\1""")

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

        def check(r, u):
            return

        desc = f"Where would you like the anime to go?\n" \
               f"Click on the Emoji related to the choice you want to make!\n\n"
        if url is not None:
            desc += f"**Title:** {name}, **Url:** [Click Me]({url})\n"
        else:
            desc += f"**Title:** {name}\n"

        desc += f"\n\n" \
                f"💖 **- Add to Favourites**\n\n" \
                f"<:CrunchyRollLogo:676087821596885013> **- Add to watchlist**\n\n" \
                f"<:9887_ServerOwner:653722257356750889> **- Add to both lists**\n\n"

        embed = discord.Embed(
            title="What list should I add it to?",
            description=desc,
            color=self.bot.colour
        )
        message = await ctx.send(embed=embed)
        BASE_EMOJIS = [
            "💖", "<:CrunchyRollLogo:676087821596885013>", "<:9887_ServerOwner:653722257356750889>"
        ]
        for emoji in BASE_EMOJIS:
            await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(TrackingAnime(bot))
