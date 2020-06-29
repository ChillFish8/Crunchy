import discord
import os
import json
import asyncio
import aiohttp
import traceback
import logging

from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from datetime import timedelta
from random import choice
from discord.ext import tasks
from concurrent import futures

from data.database import MongoDatabase
from data.cachemanager import CacheManager, Store
from logger import Logger
from data import guild_config
from resources.archieve.anime_examples import WATCHLIST

# logging.basicConfig(level=logging.INFO)

with open('config.json', 'r') as file:
    config = json.load(file)

with open('default_settings.json', 'r') as file:
    settings = json.load(file)

# Some constants we need to define before everything else.
DEFAULT_PREFIX = settings.get("prefix", "-")
TOKEN = config.get("token")
DEVELOPER_IDS = config.get("dev_ids")
SHARD_COUNT = config.get("shard_count")
COLOUR = 0xe87e15
ICON = "https://cdn.discordapp.com/app-icons/656598065532239892/39344a26ba0c5b2c806a60b9523017f3.png"

# Setup required cache to run the bot
REQUIRED_CACHE = [
    ['guilds', timedelta(minutes=60)],
    ['votes', timedelta(minutes=1)],
    ['characters', timedelta(minutes=1)],
]

# Configure logger
Logger.LOG_CACHE = False
Logger.LOG_DATABASE = False
pool = futures.ThreadPoolExecutor()


class CrunchyBot(commands.AutoShardedBot):
    def __init__(self, **options):
        super().__init__("", **options)
        self.before_invoke(self.get_config)
        self.owner_ids = DEVELOPER_IDS
        self.colour = COLOUR
        self.icon = ICON
        self.database = MongoDatabase()
        self.cache = CacheManager()
        self.error_handler = ErrorHandler()
        for collection in REQUIRED_CACHE:
            self.cache.add_cache_store(Store(name=collection[0], max_time=collection[1]))
        asyncio.get_event_loop().create_task(self.cache.background_task())
        self.started = False

    def startup(self):
        """ Loads all the commands listed in cogs folder, if there isn't a cogs folder it makes one """
        if not os.path.exists('cogs'):
            os.mkdir('cogs')

        cogs_list = os.listdir('cogs')
        if '__pycache__' in cogs_list:
            cogs_list.remove('__pycache__')

        if not config.get("dbl_voting_enabled", False):
            cogs_list.remove('top_gg_votes.py')

        for cog in cogs_list:
            try:
                self.load_extension("cogs." + cog.replace('.py', ''))
                Logger.log_info("Loaded Extension " + cog.replace('.py', ''))
            except Exception as e:
                print("Failed to load cog {cog}, Error: {e}".format(cog=cog, e=e))

        cogs_list = os.listdir('realms/cogs')
        if '__pycache__' in cogs_list:
            cogs_list.remove('__pycache__')

        for cog in cogs_list:
            try:
                self.load_extension(f"realms.cogs.{cog.replace('.py', '')}")
                Logger.log_info(f"Loaded Extension {cog.replace('.py', '')}")
            except Exception as e:
                print(f"Failed to load cog {cog}, Error: {e}")

    async def on_ready_once(self):
        pass

    async def on_shard_ready(self, shard_id):
        """ Log any shard connects """
        Logger.log_shard_connect(shard_id=shard_id)
        if not self.started:
            await self.on_ready_once()
        self.started = True

    @classmethod
    async def on_disconnect(cls):
        """ Log when we loose a shard or connection """
        Logger.log_shard_disconnect()

    async def on_command_error(self, ctx, exception):
        await self.error_handler.process_error(ctx, exception)

    def has_voted(self, user_id, force_db=False):
        if force_db:
            has_voted = self.database.get_vote(user_id)
            self.cache.store("votes", user_id, has_voted)
            if has_voted.get('expires_in', None) is not None:
                return 1
            else:
                return 0
        has_voted = self.cache.get("votes", user_id)
        if has_voted is not None:
            if has_voted.get('expires_in', None) is not None:
                return 1
            else:
                return 0
        else:
            has_voted = self.database.get_vote(user_id)
            self.cache.store("votes", user_id, has_voted)
            if has_voted.get('expires_in', None) is not None:
                return 1
            else:
                return 0

    async def get_config(self, context):
        """ Assign guild settings to context """
        if context.guild is not None:
            guild_data = self.cache.get("guilds", context.guild.id)
            if guild_data is None:
                guild_data = await self.loop.run_in_executor(pool, guild_config.GuildConfig, context.guild.id,
                                                             self.database)
                self.cache.store("guilds", context.guild.id, guild_data)
            setattr(context, 'guild_config', guild_data)
        else:
            setattr(context, 'guild_config', None)
        setattr(context, 'has_voted', self.has_voted)
        return context

    async def get_custom_prefix(self, message: discord.Message):
        """ Fetches guild data either from cache or fetches it """
        if message.guild is not None and self.user.id != 641590528026083338:
            guild_data = self.cache.get("guilds", message.guild.id)
            if guild_data is None:
                guild_data = await self.loop.run_in_executor(pool, guild_config.GuildConfig, message.guild.id,
                                                             self.database)
                self.cache.store("guilds", message.guild.id, guild_data)
            return guild_data.prefix
        else:
            return DEFAULT_PREFIX

    async def on_message(self, message):
        """ Used for case insensitive prefix """
        if not self.is_ready() or message.author.bot:
            return

        prefix = await self.get_custom_prefix(message)
        if message.content.lower().startswith(prefix.lower()):
            message.content = message.content[len(prefix):]
            await self.process_commands(message=message)

        elif message.content.startswith(f"<@{self.user.id}> "):
            message.content = message.content[len(f"<@{self.user.id}> "):]
            await self.process_commands(message=message)

        elif message.content.startswith(f"<@!{self.user.id}> "):
            message.content = message.content[len(f"<@!{self.user.id}> "):]
            await self.process_commands(message=message)


class ErrorHandler:
    def __init__(self):
        self.session = None
        self.ERROR_WEBHOOK_URL = config.get("error_webhook")
        self.webhook = None

    async def process_error(self, ctx, error):
        if self.session is None:
            self.session = aiohttp.ClientSession()
            if self.webhook is None:
                self.webhook = Webhook.from_url(self.ERROR_WEBHOOK_URL, adapter=AsyncWebhookAdapter(self.session))

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Sorry >_< I cant do that command in private messages.")

        elif isinstance(error, commands.BotMissingPermissions):
            try:
                return await ctx.author.send(
                    "<:HimeSad:676087829557936149> Sorry! It appears i cant send messages in that channel as i "
                    "am missing the permission todo so.")
            except discord.Forbidden:
                pass

        elif isinstance(error, discord.Forbidden):
            try:
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Sorry! It appears im missing permissions to do that.")
            except discord.Forbidden:
                try:
                    return await ctx.author.send(
                        "<:HimeSad:676087829557936149> Sorry! It appears im missing permissions to do that.")
                except discord.Forbidden:
                    pass

        elif isinstance(error, commands.MissingRequiredArgument):
            return

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Sorry! but that's not a user i can find.")

        elif isinstance(error, commands.MissingPermissions) and ctx.command not in (
                'addreleasechannel', 'addnewschannel', 'server_settings',
                'setprefix', 'resetprefix', 'togglensfw'):
            return await ctx.send(
                f"<:HimeSad:676087829557936149> You need to give me give me argument e.g "
                f"`{ctx.prefix}{ctx.command.name} arg1 arg2`.")

        elif ctx.command not in (
                'addreleasechannel', 'addnewschannel', 'server_settings',
                'setprefix', 'resetprefix', 'togglensfw', 'add_anime', 'recommend', 'firewall'):
            err = error
            if str(type(err).__name__) == "Forbidden" and "403" in str(err):
                return

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = ''.join(_traceback)
            full_error = '```py\n{2}{0}: {3}\n```'.format(type(err).__name__, ctx.message.content, _traceback, err)

            embed = discord.Embed(description=f"Command: {ctx.command}\n"
                                              f"Full Message: {ctx.message.content}\n"
                                              f"{full_error}",
                                  color=COLOUR)
            embed.set_author(name="Command Error.",
                             icon_url="https://cdn.discordapp.com/emojis/588404204369084456.png")
            await self.webhook.send(embed=embed)


@tasks.loop(minutes=2)
async def change_presence(bot: CrunchyBot):
    await bot.wait_until_ready()
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                            name=f"{choice(WATCHLIST)}"))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    crunchy = CrunchyBot(
        case_insensitive=True,
        fetch_offline_member=False,
        shard_count=SHARD_COUNT,
        heartbeat_timeout=60,
    )
    crunchy.startup()
    change_presence.start(crunchy)
    crunchy.run(TOKEN)
