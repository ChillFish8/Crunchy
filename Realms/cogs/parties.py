import discord
import asyncio

from discord.ext import commands

from realms.user_characters import UserCharacters

from realms.static import Database
from realms.parties import Party

class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="selectparty", aliases=['setparty'])
    async def select_party(self, ctx: commands.Context):
        user_area = UserCharacters(ctx.author.id, Database.db)
        user_party = Party(self.bot, ctx, user_area)
        await user_party.start()

    @commands.command(name="party")
    async def party(self, ctx: commands.Context):
        user_area = UserCharacters(ctx.author.id, Database.db)
        user_party = Party(self.bot, ctx, user_area)
        chars = user_party.party
        char_str = "\n".join(chars)
        embed = discord.Embed(color=self.bot.colour)
        embed.set_author(
            name=f"{ctx.author.name}'s Party",
            icon_url="https://cdn.discordapp.com/emojis/677852789074034691.png?v=1"
        )
        embed.description = char_str
        return await ctx.send(embed=embed)

    # @commands.command(name="invitetoparty", aliases=['itp', 'partyinvite', 'partyinv'])
    # async def invite_user_to_party(self, ctx: commands.Context, member: discord.User):
    #     pass

    # @commands.command(name="removefromparty", aliases=['rfp', 'remparty', 'partyremove'])
    # async def remove_from_party(self, ctx: commands.Context, member: discord.User):
    #     pass


def setup(bot):
    bot.add_cog(MarketCog(bot))
