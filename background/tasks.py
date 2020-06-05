import discord

from random import choice
from discord.ext import tasks

from resources.archieve.anime_examples import WATCHLIST

@tasks.loop(minutes=2)
async def change_presence(bot):
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                      name=f"{choice(WATCHLIST)}"))
    except:
        pass
