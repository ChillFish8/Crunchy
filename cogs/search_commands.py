import discord
import aiohttp
import random
import textwrap

from discord.ext import commands

BASE_URL = "https://legacy.crunchy.gg/api"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="animedetails", aliases=['ad', 'anime'])
    async def anime_details(self, ctx, *, query=None):
        if query is None:
            return await ctx.send(
                "<:HimeMad:676087826827444227> Oh no! You cant expect me to read your mind! "
                "You need to give me something to search for!")

        async with aiohttp.ClientSession() as sess:
            async with sess.get(
                    "https://api.crunchy.gg/v0/data/anime/search",
                    params={"query": query, "limit": "1"}
            ) as resp:
                if resp.status != 200:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                          "Something seems to have gone wrong when searching for that."
                                          " Please try again later!")
                details = (await resp.json())['data']['hits']
                if len(details) == 0:
                    return await ctx.send(
                        "<:HimeSad:676087829557936149> Oh no! "
                        "I couldn't find what you are searching for."
                    )

        first = details[0]
        title = first['title_english'] or first['title']
        description = first['description'] or "No Description."
        genres = first['genres']
        rating = int(first['rating'] / 2)
        img_url = first['img_url']

        stars = "⭐" * rating
        genres = ", ".join(genres)

        embed = discord.Embed(
            title=f"{textwrap.shorten(title, width=80)}",
            color=self.bot.colour
        )
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_image(url=img_url)
        embed.set_footer(
            text="Part of Crunchy, the Crunchyroll Discord bot. Powered by CF8",
            icon_url=ctx.author.avatar_url,
        )

        embed.description = f"**Rating:** {stars}\n" \
                            f"**Genres:** {genres}\n" \
                            f"\n" \
                            f"**Description:**\n {textwrap.shorten(description, width=300)}\n"
        return await ctx.send(embed=embed)

    @commands.command(name="mangadetails", aliases=['md', 'manga'])
    async def manga_details(self, ctx, *, query=None):
        if query is None:
            return await ctx.send(
                "<:HimeMad:676087826827444227> Oh no! You cant expect me to read your mind! "
                "You need to give me something to search for!")

        async with aiohttp.ClientSession() as sess:
            async with sess.get(
                    "https://api.crunchy.gg/v0/data/manga/search",
                    params={"query": query, "limit": "1"},
            ) as resp:
                if resp.status != 200:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                          "Something seems to have gone wrong when searching for that."
                                          " Please try again later!")
                details = (await resp.json())['data']['hits']
                if len(details) == 0:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                          "I couldn't find what you are searching for.")

        first = details[0]
        title = first['title_english'] or first['title']
        description = first['description'] or "No Description."
        genres = first['genres']
        rating = int(first['rating'] / 2)
        img_url = first['img_url']

        stars = "⭐" * rating
        genres = ", ".join(genres)

        embed = discord.Embed(
            title=f"{textwrap.shorten(title, width=80)}",
            color=self.bot.colour
        )
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_image(url=img_url)
        embed.set_footer(
            text="Part of Crunchy, the Crunchyroll Discord bot. Powered by CF8",
            icon_url=ctx.author.avatar_url,
        )

        embed.description = f"**Rating:** {stars}\n" \
                            f"**Genres:** {genres}\n" \
                            f"\n" \
                            f"**Description:**\n {textwrap.shorten(description, width=300)}\n"
        return await ctx.send(embed=embed)

    @commands.command(name="webtoondetails", aliases=['wtd', 'wt', 'webtoon'])
    async def webtoon_details(self, ctx, *args):
        if len(args) <= 0:
            return await ctx.send(
                "<:HimeMad:676087826827444227> Oh no! You cant expect me to read your mind! "
                "You need to give me something to search for!")

        details_url = BASE_URL + "/webtoon/details?terms={}"
        url = details_url.format("+".join(args))
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                          "Something seems to have gone wrong when searching for that."
                                          " Please try again later!")
                else:
                    details = await resp.json()
                    if len(details) >= 1:
                        details = details[0]
                    else:
                        return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                              "I couldn't find what you are searching for.")

        embed = discord.Embed(
            title=f"<:webtoon:742857781232795741>  {details['title']}  <:webtoon:742857781232795741>",
            url=details.get('url'),
            color=self.bot.colour
        )
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        if details.get('banner_src'):
            embed.set_image(url=details.get('banner_src'))
        embed.set_footer(text="Part of Crunchy, the Crunchyroll Discord bot. Powered by CF8",
                         icon_url=ctx.author.avatar_url)
        embed.description = f"" \
                            f"⭐ **Rating** {details.get('rating', 'unknown')} / 10\n\n" \
                            f"📖 **Subscribers** {details.get('subscribers', '0')}\n\n"
        embed.add_field(
            name="Description",
            value=details.get('summary', 'No Description.')[
                  :500] + f" [read now]({details.get('first_ep_url', '')})",
            inline=False)

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Search(bot))
