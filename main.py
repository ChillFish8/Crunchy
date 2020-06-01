import discord
import os
import json
from discord.ext import commands

from database.database import MongoDatabase
from database.cachemanager import CacheManager
from logger import Logger


with open('config.json', 'r') as file:
    config = json.load(file)

DEFAULT_PREFIX = ['?']
TOKEN = config.get("token")
DEVELOPER_IDS = config.get("dev_ids")
SHARD_COUNT = config.get("shard_count")


class CrunchyBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.owner_ids = DEVELOPER_IDS
        self.colour = 0xe1552a
        self.icon = "https://cdn.discordapp.com/app-icons/656598065532239892/39344a26ba0c5b2c806a60b9523017f3.png"
        self.database = MongoDatabase()
        self.cache = CacheManager()

    def startup(self):
        """ Loads all the commands listed in cogs folder, if there isn't a cogs folder it makes one """
        if not os.path.exists('cogs'):
            os.mkdir('cogs')

        cogs_list = os.listdir('cogs')
        if '__pycache__' in cogs_list:
            cogs_list.remove('__pycache__')

        for cog in cogs_list:
            try:
                self.load_extension(f"cogs.{cog.replace('.py', '')}")
            except Exception as e:
                print(f"Failed to load cog {cog}, Error: {e}")
                raise e

    @classmethod
    async def on_shard_ready(cls, shard_id):
        """ Log any shard connects """
        Logger.log_shard_connect(shard_id=shard_id)

    @classmethod
    async def on_disconnect(cls):
        """ Log when we loose a shard or connection """
        Logger.log_shard_disconnect()

    async def get_config(self, context):
        """ Assign guild settings to context """
        if context.guild is not None:
            guild_data = self.cache.get("GUILD", context.guild.id)
            if guild_data is None:
                guild_data = self.database.fetch_guild(context.guild.id)
                self.cache.store("GUILD", context.guild.id, guild_data)
            setattr(context, 'config', guild_data)
        return context

    async def get_custom_prefix(self, bot, message: discord.Message):
        """ Fetches guild data either from cache or fetches it """
        if message.guild is not None:
            guild_data = self.cache.get("GUILD", message.guild.id)
            if guild_data is None:
                guild_data = self.database.fetch_guild(message.guild.id)
                self.cache.store("GUILD", message.guild.id, guild_data)
            return guild_data.prefix
        else:
            return DEFAULT_PREFIX

    async def on_message(self, message):
        """ Used for some events later on """
        await self.process_commands(message=message)


Logger.log_shard_disconnect()
Logger.log_shard_connect(1)
Logger.log_info("Hello World!")
