from discord.ext import commands

from data.guild_config import GuildConfig

class Customisations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



def setup(bot):
    bot.add_cog(Customisations(bot))
