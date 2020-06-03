import re

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
        else:
            name, url = items[0], None





def setup(bot):
    bot.add_cog(TrackingAnime(bot))
