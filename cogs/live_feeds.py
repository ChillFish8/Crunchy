import discord
import aiohttp
import asyncio
import feedparser
import random
import textwrap
import concurrent.futures
import io
import time
import requests

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from colorama import Fore
from bs4 import BeautifulSoup

from data.database import MongoDatabase
from data.guild_config import GuildWebhooks
from logger import Logger, Timer

# Urls
RELEASE_RSS = "http://feeds.feedburner.com/crunchyroll/rss/anime"
NEWS_RSS = "http://feeds.feedburner.com/crunchyroll/animenews"
API_BASE = "https://crunchy-bot.live/api/anime"

# Black list
EXCLUDE_IN_TITLE = [
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
RANDOM_EMOJIS = [
    '<:thank_you:717784142053507082>',
    '<:cheeky:717784139226546297>',
    '<:exitment:717784139641651211>',
]

PFP_PATH = r'resources/photos/crunchy_image.png'


class MicroGuildWebhook:
    def __init__(self, guild_id, url, mentions=None):
        self.guild_id = guild_id
        self.url = url
        if mentions is not None:
            mentions = "__**Release Ping**__" + ", ".join(mentions)
        self.content = mentions


class WebhookBroadcast:
    def __init__(self, database: MongoDatabase, embed: discord.Embed,
                 web_hooks: list, type_: str, title: str, name="Crunchy", buffer=None):
        self.embed = embed
        self.web_hooks = web_hooks
        self.failed_to_send = []
        self.session = None
        self.name = name
        self.type = type_
        self.successful = 0
        self.title = title
        self.database = database
        self.buffer = buffer

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        Logger.log_broadcast(f"Cleaning up broadcast, deleting {len(self.failed_to_send)} hooks.")
        for fail in self.failed_to_send:
            hook_object = GuildWebhooks(guild_id=fail, database=self.database)
            # hook_object.delete_webhook(feed_type=self.type.lower())
        await self.session.close()

    async def send_func(self, hook: MicroGuildWebhook):
        try:
            webhook = Webhook.from_url(hook.url, adapter=AsyncWebhookAdapter(self.session))
            if self.buffer is not None:
                self.buffer.seek(0)
                file = discord.File(fp=self.buffer, filename="NewNews.png")
            else:
                file = None
            await webhook.send(embed=self.embed, file=file, content=hook.content, username=self.name)
            self.successful += 1

        except discord.InvalidArgument:
            self.failed_to_send.append(hook.guild_id)

        except discord.NotFound:
            self.failed_to_send.append(hook.guild_id)

        except Exception as e:
            print(e)

    async def broadcast(self):
        chunks, remaining = divmod(len(self.web_hooks), 10)
        for i in range(chunks):
            tasks = []
            for guild in self.web_hooks[i * 10:i * 10 + 10]:
                if guild.url is not None:
                    tasks.append(self.send_func(hook=guild))
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.75)
        else:
            await asyncio.sleep(0.75)
            tasks = []
            for guild in self.web_hooks[::-1][:remaining]:
                if guild.url is not None:
                    tasks.append(self.send_func(hook=guild))
            await asyncio.gather(*tasks)
        self.title = self.title.replace('\n', '')
        Logger.log_broadcast(f'[ {self.type} ] Completed broadcast of "{self.title}"!')
        Logger.log_broadcast(f"[ {self.type} ]          {self.successful} messages sent!")


def map_objects_releases(data):
    data = data['config']
    id_ = data.get('guild_id', data.get('user_id', data.get('guid_id', )))
    guild = MicroGuildWebhook(id_, data['release'])
    return guild

def map_objects_news(data):
    data = data['config']
    id_ = data.get('guild_id', data.get('user_id', data.get('guid_id', )))
    guild = MicroGuildWebhook(id_, data['news'])
    return guild


class LiveFeedBroadcasts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.to_send = []
        self.sent = []
        self.processed_releases = []
        self.processed_news = []
        self.callbacks = {'release': self.release_callback, 'payload': self.news_callback}
        self.loop.create_task(self.background_checker())
        self.first_start = True

    async def background_checker(self):
        while True:
            await self.bot.wait_until_ready()
            if self.first_start:
                await asyncio.sleep(600)
                self.first_start = False
            async with aiohttp.ClientSession() as sess:
                async with sess.get(RELEASE_RSS) as resp_release:
                    if resp_release.status == 200:
                        content = await resp_release.text()
                        release_parser = feedparser.parse(content)['entries'][0]
                        if not any([item in release_parser['title'].lower() for item in EXCLUDE_IN_TITLE]):
                            if release_parser['id'] not in self.processed_releases:
                                self.processed_releases.append(release_parser['id'])
                                self.to_send.append({'type': 'release', 'rss': release_parser})
                                Logger.log_rss(
                                    """[ RELEASE ]  Added "{}" to be sent!""".format(release_parser['title']))

                async with sess.get(NEWS_RSS) as resp_news:
                    if resp_release.status == 200:
                        content = await resp_news.text()
                        news_parser = feedparser.parse(content)['entries'][0]
                        if not any([item in news_parser['title'].lower() for item in EXCLUDE_IN_TITLE]):
                            if news_parser['id'] not in self.processed_news:
                                self.processed_news.append(news_parser['id'])
                                self.to_send.append({'type': 'payload', 'rss': news_parser})
                                Logger.log_rss("""[ NEWS ]  Added "{}" to be sent!""".format(news_parser['title']))
            await self.process_payloads()
            await asyncio.sleep(600)

    async def process_payloads(self):
        for item in self.to_send:
            asyncio.get_event_loop().create_task(self.callbacks[item['type']](item['rss']))
        self.to_send = []

    async def release_callback(self, rss: dict):
        first = rss['title'].split(" - ")[0]
        terms = first.lower().split(" ")
        details = await self.get_release_info(terms=terms)
        if details is None:
            return
        else:
            anime_details = details['details']['data']
            embed = self.make_release_embed(anime_details, rss, rss['title'].split(" - "))
            guilds = self.bot.database.get_all_webhooks()
            web_hooks = list(map(map_objects_releases, guilds))
            async with WebhookBroadcast(
                    embed=embed, web_hooks=web_hooks, type_="RELEASES",
                    title=anime_details['title'], database=self.bot.database) as broadcast:
                await broadcast.broadcast()

    @staticmethod
    def make_release_embed(details: dict, rss: dict, first):
        embed = discord.Embed(
            title=f"{rss['title']}", url=rss.get('id', None), color=COLOUR)
        desc = f"⭐ **Rating:** {details['reviews']} / 5 stars\n" \
               f"[Read the reviews here!]" \
               f"({'https://www.crunchyroll.com/{}/reviews'.format(details['title'].lower().replace(' ', '-'))})\n" \
               f"\n" \
               f"📌 **[{first[1]}]({rss['id']})**\n" \
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
                    if result['status'] == 404:
                        Logger.log_rss(
                            Fore.RED + f"[ ERROR ] "
                            f"Api GET request failed to returned searched anime.",
                            error=True)
                        return
                else:
                    Logger.log_rss(
                        Fore.RED + f"[ ERROR ] "
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
        title = "\n".join(textwrap.wrap(rss['title'], width=42))
        soup = BeautifulSoup(rss['summary'].replace("<br/>", "||", 1).replace("\xa0", " "), 'lxml')
        split = soup.text.split("||", 1)
        summary, brief = split
        brief = "\n".join(textwrap.wrap(brief, width=50)[:6])
        brief += "..."
        img_url = soup.find('img').get('src')

        payload = {
            'title': title,
            'img_url': img_url,
            'summary': summary,
            'brief': brief,
            'url': rss['id']
        }
        start = time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            buffer = await self.loop.run_in_executor(pool, self.generate_news_image, payload)
        delta = time.time() - start
        Timer.timings['LiveFeedBroadcasts.news_callback'] = delta

        embed = discord.Embed(
            description=f"[Read More]({payload['url']}) | "
                        f""
                        f" [Vote for Crunchy](https://top.gg/bot/656598065532239892)\n",
            color=0xe87e15,
            timestamp=datetime.now())
        embed.set_footer(text="Part of Crunchy, the Crunchyroll bot. Powered by CF8")
        embed.set_author(name="Crunchyroll Anime News! - Click for more!",
                         icon_url="https://cdn.discordapp.com/emojis/656236139862032394.png?v=1",
                         url=f"{payload['url']}")
        embed.set_image(url="attachment://NewNews.png")

        guilds = self.bot.database.get_all_webhooks()
        web_hooks = list(map(map_objects_news, guilds))
        async with WebhookBroadcast(
                embed=embed, web_hooks=web_hooks, type_="NEWS",
                title=payload['title'], database=self.bot.database, buffer=buffer) as broadcast:
            await broadcast.broadcast()

    @staticmethod
    def generate_news_image(payload):
        original = Image.open("resources/webhooks/images/background.png")

        edited = ImageDraw.Draw(original)

        y_pos_diff = 35 * payload['title'].count("\n")
        title = payload['title']

        # Title
        edited.text((20, 20),
                    text=title,
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=32)
                    )

        # Episode / payload summary
        edited.text((20, (60 + y_pos_diff)),
                    text=f'''"{payload['summary']}"''',
                    fill=(102, 102, 102),
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial Italic/Arial Italic.ttf",
                        size=16)
                    )

        # Timestamp
        edited.text((20, (120 + y_pos_diff)),
                    text=datetime.now().strftime('%B, %d %Y %I:%M%p BST'),
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )

        # break line
        edited.line(((20, (145 + y_pos_diff)), (680, (145 + y_pos_diff))),
                    fill=(226, 226, 226),
                    width=1)

        # icon
        r = requests.get(payload['img_url'])
        buffer = io.BytesIO()
        buffer.write(r.content)
        buffer.seek(0)
        icon = Image.open(buffer)
        original.paste(icon, (20, 160 + y_pos_diff))

        # desc
        desc = payload['brief']
        edited.text((195, (160 + y_pos_diff)),
                    text=str(desc),
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )

        # Crunchy logo n stuff
        icon = Image.open(r"resources/webhooks/images/crunchy_image.png")
        icon = icon.resize((60, 60))
        original.paste(icon, (620, (70 + y_pos_diff)), icon)

        edited.text((350, (120 + y_pos_diff)),
                    text="Powered by Crunchy Discord bot.",
                    fill="black",
                    font=ImageFont.truetype(
                        r"resources/webhooks/fonts/Arial/Arial.ttf",
                        size=18)
                    )

        buffer = io.BytesIO()
        original.save(buffer, "png")
        return buffer


class LiveFeedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def check_exists(cls, name, hooks):
        """ Getting current web hooks """
        for hook in hooks:
            if name.lower().replace(" ", "") in hook.name.lower().replace(" ", ""):
                return hook.name
        else:
            return False

    @classmethod
    async def make_webhook(cls, channel, feed_type):
        with open(PFP_PATH, 'rb') as file:
            new_webhook = await channel.create_webhook(
                name=f'Crunchyroll {feed_type.capitalize()}', avatar=file.read())
            return new_webhook

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addreleasechannel", aliases=['arc', 'addrelease'])
    async def add_release_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Lest just make sure they cant have multiple hooks at once
        check = self.check_exists(name="Crunchyroll Releases", hooks=existing_hooks)
        if check:
            return await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a release webhook (`{check}`) active.\n"
                f"Please delete the original release webhook first.")

        to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
        guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
        try:
            webhook = await self.make_webhook(channel=channel, feed_type="releases")
            guild_data.add_webhook(webhook=webhook, feed_type="releases")
            await webhook.send(content=random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
            return await to_edit.edit(content=f'All set! I will now send releases to <#{webhook.channel_id}>')
        except discord.Forbidden:
            return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                              "I need the permission `MANAGE_WEBHOOKS`.")
        except AttributeError:
            return await to_edit.edit(
                content="Sorry but something went wrong when trying to make this webhook."
                        " Please try a different channel.")

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addnewschannel", aliases=['acc', 'addnews'])
    async def add_news_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Lest just make sure they cant have multiple hooks at once
        check = self.check_exists(name="Crunchyroll News", hooks=existing_hooks)
        if check:
            return await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a news webhook (`{check}`) active.\n"
                f"Please delete the original release webhook first.")
        to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
        guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
        try:
            webhook = await self.make_webhook(channel=channel, feed_type="news")
            guild_data.add_webhook(webhook=webhook, feed_type="news")
            await webhook.send(content=random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
            return await to_edit.edit(content=f'All set! I will now send payload to <#{webhook.channel_id}>')
        except discord.Forbidden:
            return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                              "I need the permission `MANAGE_WEBHOOKS`.")
        except AttributeError:
            return await to_edit.edit(
                content="Sorry but something went wrong when trying to make this webhook."
                        " Please try a different channel.")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Sorry! You're missing the require permission `ADMINISTRATOR`"
                f"to use this command (`{ctx.command}`)")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> You need to mention a channel"
                " or give me a channel Id for this command.")

def setup(bot):
    bot.add_cog(LiveFeedCommands(bot))
    bot.add_cog(LiveFeedBroadcasts(bot))


# Testing area only:
async def main():
    test = LiveFeedBroadcasts("owo")
    await test.background_checker()


if __name__ == "__main__":
    asyncio.run(main())
