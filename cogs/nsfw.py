import aiohttp
import asyncio
import discord

from discord.ext import commands

CRUNCHY_API_BASE = "https://crunchy-bot.live/api"
NEKO_API_BASE = "https://nekobot.xyz/api"  # todo replace with Crunchy api
THUMB_IMG = "https://cdn.discordapp.com/emojis/717784142053507082.png?v=1"


class ApiCollectors:
    def __init__(self):
        self.session = None
        asyncio.get_event_loop().create_task(self.activate())

    async def activate(self):
        self.session = aiohttp.ClientSession()

    async def get_from_neko(self, type_):
        async with self.session.get((NEKO_API_BASE + f"/image?type={type_}")) as r:
            result = await r.json()
            return result

    async def get_from_crunchy(self, tag=None, type_="hentai"):
        url = CRUNCHY_API_BASE + f"/nsfw/{type_}"
        if tag is not None:
            url += f"?tag={tag}"
        async with self.session.get(url) as r:
            result = await r.json()
            return result


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collector = ApiCollectors()
        self.NSFW_HENTAI_TAGS = [
            # 'ass': os.listdir(f"{base}hentai/ass"),
            'big_boobs',
            'creampie',
            'lingeries',
            'monster_girls',
            'solo',
            'tenticles',
            'underwear',
            'yuri',
        ]

    @commands.command()
    async def hentai(self, ctx, tag: str = None):
        if not ctx.channel.is_nsfw():
            return await ctx.send(
                "<:cheeky:717784139226546297> Oops! NSFW comm"
                "ands can only be used in NSFW channels.")

        if ctx.has_voted(ctx.author.id) >= 1:
            if ctx.guild is not None:
                if not ctx.guild_config.nsfw_enabled:
                    return await ctx.send(
                        "<:cheeky:717784139226546297> Oops! NSFW is disabled in this server,"
                        " ask a admin to run `togglensfw` if"
                        " this should be enabled.")

            resp = await self.collector.get_from_crunchy(tag=tag)
            embed = discord.Embed(color=self.bot.colour)
            embed.set_image(url=resp['url'])
            embed.set_footer(text="https://legacy.crunchy.gg/api/endpoints")
            await ctx.send(embed=embed)
        else:
            await self.send_vote(ctx)

    @commands.command()
    async def ass(self, ctx):
        if not ctx.channel.is_nsfw():
            return await ctx.send("<:cheeky:717784139226546297> Oops! NSFW commands can only be "
                                  "used in NSFW channels.")

        if ctx.has_voted(ctx.author.id) >= 1:
            if ctx.guild is not None:
                if not ctx.guild_config.nsfw_enabled:
                    return await ctx.send(
                        "<:cheeky:717784139226546297> Oops! NSFW is disabled in this server,"
                        " ask a admin to run `togglensfw` if this should be enabled.")
            resp = await self.collector.get_from_neko(type_="ass")
            await self.send_embed(ctx, resp['message'])
        else:
            await self.send_vote(ctx)

    @commands.command()
    async def pussy(self, ctx):
        if not ctx.channel.is_nsfw():
            return await ctx.send(
                "<:cheeky:717784139226546297> Oops! NSFW commands c"
                "an only be used in NSFW channels.")

        if ctx.has_voted(ctx.author.id) >= 1:
            if ctx.guild is not None:
                if not ctx.guild_config.nsfw_enabled:
                    return await ctx.send(
                        "<:cheeky:717784139226546297> Oops! NSFW is disabled in this server,"
                        " ask a admin to run `togglensfw` if this should be enabled.")
            resp = await self.collector.get_from_neko(type_="pussy")
            await self.send_embed(ctx, resp['message'])
        else:
            await self.send_vote(ctx)

    @commands.command(name="gonewild")
    async def gone_wild(self, ctx):
        if not ctx.channel.is_nsfw():
            return await ctx.send(
                "<:cheeky:717784139226546297> Oops! NSFW comma"
                "nds can only be used in NSFW channels.")

        if ctx.has_voted(ctx.author.id) >= 1:
            if ctx.guild is not None:
                if not ctx.guild_config.nsfw_enabled:
                    return await ctx.send(
                        "<:cheeky:717784139226546297> Oops! NSFW is disabled in this server,"
                        " ask a admin to run `togglensfw` if this should be enabled.")
            resp = await self.collector.get_from_neko(type_="gonewild")
            await self.send_embed(ctx, resp['message'])
        else:
            await self.send_vote(ctx)

    async def send_embed(self, ctx, url):
        embed = discord.Embed(color=self.bot.colour)
        embed.set_image(url=url)
        embed.set_footer(text="https://nekobot.xyz/api/")
        await ctx.send(embed=embed)

    async def send_vote(self, ctx):
        embed = discord.Embed(
            color=self.bot.colour,
            title="Vote to support us! ",
            description="Vote here to get access to NSFW and more for 24 hours:\n"
                        "**[Vote for me](https://top.gg/bot/656598065532239892/vote)**\n")
        embed.set_thumbnail(url=THUMB_IMG)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NSFW(bot))
