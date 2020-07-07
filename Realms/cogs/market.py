import discord

from discord.ext import commands

from realms.static import Database
from realms.user_characters import UserCharacters


class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['balance', 'bal'])
    async def pocket(self, ctx: commands.Context):
        user_area = UserCharacters(ctx.author.id, Database.db)
        embed = discord.Embed(color=self.bot.colour)
        embed.set_author(name=f"{ctx.author.name}'s Adventures Bank", icon_url=ctx.author.avatar_url)
        embed.description = f"\💠 **Platinum Pieces -** `{user_area.platinum}pp`\n" \
                            f"\🔹 **Gold Pieces -** `{user_area.gold}gp`\n" \
                            f"\🔸**Copper Pieces -** `{user_area.copper}cp`\n"
        embed.set_footer(text="You can earn money by completing quests and voting.")
        await ctx.send(embed=embed)

    @commands.command(name="encounter")
    async def encounter(self, ctx: commands.Context):
        pass

    



def setup(bot):
    bot.add_cog(MarketCog(bot))
