import discord
import aiohttp

from discord.ext import commands


BASE_URL = "https://crunchy-bot.live/api"

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
                            if resp.status != 200:
                                return await ctx.send("<:HimeSad:676087829557936149> Oh no! "
                                                      "Something seems to have gone wrong when searching for that."
                                                      " Please try again later!")
                            else:
                                details = await resp.json()



def setup(bot):
    bot.add_cog(Search(bot))