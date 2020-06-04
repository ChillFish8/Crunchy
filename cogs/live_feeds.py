import discord
import aiohttp
import asyncio
import feedparser
import random

from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from colorama import Fore

from logger import Logger

# Urls
RELEASE_RSS = "http://feeds.feedburner.com/crunchyroll/rss"
NEWS_RSS = "http://feeds.feedburner.com/crunchyroll/animenews"
API_BASE = "https://crunchy-bot.live/api/anime"

# Black list
EXCLUDE_IN_TITLE =[
    'dub)',
    '(russian',
    '(spanish',
]

# Embed Option
COLOUR = 0xe87e15
CR_LOGO = "https://cdn.discordapp.com/emojis/676087821596885013.png?v=1"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]


class GuildWebhook:
    def __init__(self, guild_id, url, mentions=None):
        self.guild_id = guild_id
        self.url = url
        if mentions is not None:
            mentions = "__**Release Ping**__" + ", ".join(mentions)
        self.content = mentions


class WebhookBroadcast:
    def __init__(self, embed: discord.Embed, web_hooks: list, type_, name="Crunchy"):
        self.embed = embed
        self.web_hooks = web_hooks
        self.failed_to_send = []
        self.session = None
        self.name = name
        self.type = type_

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        Logger.log_broadcast(f"Cleaning up broadcast, deleting {len(self.failed_to_send)} hooks.")
        await self.session.close()

    async def send_func(self, hook: GuildWebhook):
        try:
            webhook = Webhook.from_url(hook.url, adapter=AsyncWebhookAdapter(self.session))
            await webhook.send(embed=self.embed, content=hook.content, username=self.name)

        except discord.InvalidArgument:
            self.failed_to_send.append(hook.guild_id)

        except discord.NotFound:
            self.failed_to_send.append(hook.guild_id)

    async def broadcast(self):
        for i in range(1, len(self.web_hooks), 250):
            tasks = []
            for guild in self.web_hooks[i:i + 250]:
                tasks.append(self.send_func(hook=guild))
            await asyncio.gather(*tasks)
        Logger.log_broadcast(f"[ {self.type} ] Completed broadcast!")
        Logger.log_broadcast(f"[ {self.type} ]             {len(self.web_hooks)} messages sent!")


def map_objects_releases(data):
    guild = GuildWebhook(data['guild_id'], data['release'])
    return guild


class LiveFeedBroadcasts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.to_send = []
        self.sent = []
        self.processed = []
        self.callbacks = {'release': self.release_callback, 'news': self.news_callback}

    async def background_checker(self):
        while True:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(RELEASE_RSS) as resp_release:
                    if resp_release.status == 200:
                        content = await resp_release.text()
                        release_parser = feedparser.parse(content)['entries'][3]
                        if not any([item in release_parser['title'].lower() for item in EXCLUDE_IN_TITLE]):
                            if release_parser['id'] not in self.processed:
                                self.processed.append(release_parser['id'])
                                self.to_send.append({'type': 'release', 'rss': release_parser})
                                Logger.log_rss("""[ RELEASE ]  Added "{}" to be sent!""".format(release_parser['title']))

                async with sess.get(NEWS_RSS) as resp_news:
                    if resp_release.status == 200:
                        content = await resp_news.text()
                        news_parser = feedparser.parse(content)['entries'][0]
                        if not any([item in news_parser['title'].lower() for item in EXCLUDE_IN_TITLE]):
                            if news_parser['id'] not in self.processed:
                                self.processed.append(news_parser['id'])
                                self.to_send.append({'type': 'news', 'rss': news_parser})
                                Logger.log_rss("""[ NEWS ]  Added "{}" to be sent!""".format(news_parser['title']))
            self.loop.create_task(self.process_payloads())
            await asyncio.sleep(300)

    async def process_payloads(self):
        for item in self.to_send:
            await self.callbacks[item['type']](item['rss'])

    async def release_callback(self, rss: dict):
        first = rss['title'].split(" - ")[0]
        terms = first.lower().split(" ")
        details = await self.get_release_info(terms=terms)
        if details is None:
            return
        else:
            anime_details = details['details']['data']
            embed = self.make_release_embed(anime_details, rss, first)
            guilds = self.bot.database
            web_hooks = list(map(map_objects_releases, guilds))
            async with WebhookBroadcast(embed=embed, web_hooks=web_hooks, type_="RELEASE") as broadcast:
                await broadcast.broadcast()

    @staticmethod
    def make_release_embed(details: dict, rss: dict, first):
        embed = discord.Embed(
            title=f"{rss['title']}", url=rss.get('id', None), color=COLOUR)
        desc = f"⭐ **Rating:** {details['reviews']} / 5 stars\n" \
               f"[Read the reviews here!]" \
               f"({'https://www.crunchyroll.com/{}/reviews'.format(details['title'].lower().replace(' ', '-'))})\n" \
               f"\n" \
               f"**[{first[1]}]({rss['id']})**\n" \
               f"\n" \
               f"**Description:**\n" \
               f"{details['desc_long']}\n"
        embed.description = desc
        embed.set_image(url=details['thumb_img'])
        embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
        embed.set_footer(text="Anime releases from Crunchyroll. Bot powered by CF8")
        embed.set_author(name="Crunchyroll New Release! - Click for more!", url=rss.get('id', None), icon_url=CR_LOGO)
        return embed

    @classmethod
    async def get_release_info(cls, terms: list):
        url = API_BASE + "/search?terms=" + "+".join(terms) + "&legacy=True"

        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                else:
                    Logger.log_rss(
                        Fore.RED + f"[ ERROR ] " + Fore.WHITE +
                        f"Api GET request failed with status {resp.status}",
                        error=True)
                    return
                details_url = API_BASE + f"/details?id={result['result_id']}"
            async with sess.get(details_url) as details_resp:
                if details_resp.status == 200:
                    details = await details_resp.json()
                    return details
                else:
                    Logger.log_rss(
                        Fore.RED + f"[ ERROR ] " + Fore.WHITE +
                        f"Api GET request failed with status {resp.status}",
                        error=True)
                    return

    async def news_callback(self, rss: dict):
        pass


class LiveFeedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(LiveFeedBroadcasts(bot))
    bot.add_cog(LiveFeedCommands(bot))


# Testing area only:
async def main():
    test = LiveFeedBroadcasts("owo")
    await test.background_checker()

if __name__ == "__main__":
    asyncio.run(main())
