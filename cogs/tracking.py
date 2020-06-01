from discord.ext import commands

from database.database import GuildConfig

class TrackingAnime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



def setup(bot):
    bot.add_cog(TrackingAnime(bot))
