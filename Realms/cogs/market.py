from discord.ext import commands

from realms.datastores.database import MongoDatabase
from realms.static import Database


class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(MarketCog(bot))
