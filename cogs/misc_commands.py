import discord
import aiohttp
import random

from discord.ext import commands

BASE_URL = "https://legacy.crunchy.gg/api"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="todayspicks", aliases=['picks', 'dailyanime', 'tp'])
    async def anime_details(self, ctx):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{BASE_URL}/anime/daily") as resp:
                if resp.status != 200:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! Something seems to have gone wrong,"
                                          " please try again later.")
                else:
                    listed_items = await resp.json()

        embed = discord.Embed(color=self.bot.colour)
        for i, anime in enumerate(listed_items):
            url_safe = anime.get('title').replace(" ", "-").replace(".", "").replace(":", "")
            url = "https://www.crunchyroll.com/{}".format(url_safe)
            embed.add_field(name="\u200b", value=f"**{i + 1} ) - [{anime.get('title')}]({url})**", inline=False)
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_footer(text="Part of Crunchy, Powered by CF8")
        embed.set_author(name="Today's Anime Picks!", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
