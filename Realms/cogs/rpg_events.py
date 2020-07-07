import random
import asyncio
import discord

from typing import Union
from discord.ext import commands
from discord.ext import tasks


from realms.static import Database

HAPPY_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png",
    "https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png"
]
SAD_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784461391167568/sad.png",
]

START_PANEL = discord.Embed(title="Mini-Games")


class LevelUpGames(commands.Cog):
    database = Database.db

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.on_event.start()

    async def get_channel(self, guild_id, channel_id) -> Union[int, discord.TextChannel]:
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
                if not isinstance(channel, discord.TextChannel):
                    raise discord.InvalidData()
            except (discord.NotFound, discord.Forbidden, discord.InvalidData):
                self.database.delete_event(guild_id)
                return -1
        return channel

    @tasks.loop(minutes=10)
    async def on_event(self):
        all_events = self.database.get_all_events()
        for event_guild in all_events():
            resp = await self.get_channel(**event_guild)
            if resp == -1:
                continue
            else:
                if random.randint(1, 20) == 2:
                    resp = await self.send_event(event_guild)
                    if resp != -1:
                        await asyncio.sleep(2)

    async def send_event(self, event_guild):
        pass


def setup(bot):
    pass
    # bot.add_cog(LevelUpGames(bot))
