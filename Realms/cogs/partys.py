import discord

from discord.ext import commands

from realms.datastores.database import MongoDatabase
from realms.static import Database


class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="selectparty", aliases=['setparty'])
    async def select_party(self, ctx: commands.Context):
        pass

    @commands.command(name="party")
    async def party(self, ctx: commands.Context):
        pass

    @commands.command(name="invitetoparty", aliases=['itp', 'partyinvite', 'partyinv'])
    async def invite_user_to_party(self, ctx: commands.Context, member: discord.User):
        pass

    @commands.command(name="removefromparty", aliases=['rfp', 'remparty', 'partyremove'])
    async def remove_from_party(self, ctx: commands.Context, member: discord.User):
        pass


def setup(bot):
    bot.add_cog(MarketCog(bot))
