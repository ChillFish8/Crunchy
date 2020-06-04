import discord
import aiohttp
import random

from discord.ext import commands


BASE_URL = "https://crunchy-bot.live/api"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="animedetails", aliases=['ad'])
    async def anime_details(self, ctx, *args):
        if len(args) <= 0:
            return await ctx.send("<:HimeMad:676087826827444227> Oh no! You cant expect me to read your mind! "
                                  "You need to give me something to search for!")

        search_url = BASE_URL + "/anime/search?legacy=True&terms=" + "+".join(args)
        details_url = BASE_URL + "/anime/details?id={}"
        async with aiohttp.ClientSession() as sess:
            async with sess.get(search_url) as resp:
                if resp.status != 200:
                    return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                          "Something seems to have gone wrong when searching for that."
                                          " Please try again later!")
                else:
                    results = await resp.json()
                    if results.get("status", 404) != 200:
                        return await ctx.send("<:HimeSad:676087829557936149> Oops! "
                                              "I couldn't find what you were search for.")
                    else:
                        async with sess.get(details_url.format(results['result_id'])) as resp_2:
                            if resp_2.status != 200:
                                return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                                      "Something seems to have gone wrong when searching for that."
                                                      " Please try again later!")
                            else:
                                details = await resp_2.json()
                                details = details['details']['data']
        embed = discord.Embed(
            title=f"<:CrunchyRollLogo:676087821596885013>  {details['title']}  <:CrunchyRollLogo:676087821596885013>",
            url=f"https://www.crunchyroll.com/{details['title'].lower().replace(' ', '-')}",
            color=self.bot.colour
        )
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_image(url=details['thumb_img'])
        embed.set_footer(text="Part of Crunchy, the Crunchyroll Discord bot. Powered by CF8",
                         icon_url=ctx.author.avatar_url)

        embed.description = f"⭐ **Rating** {details['reviews']} / 5 stars\n" \
                            f"\n" \
                            f"__**Description:**__\n {details['desc_long']}\n"
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Search(bot))