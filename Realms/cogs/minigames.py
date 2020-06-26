import json
import random
import time
import discord

from datetime import datetime
from discord.ext import commands
from discord.ext import tasks

from realms.character import Character
from realms.user_characters import UserCharacters
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
        self.bot = bot

    @commands.command(name="minigame", aliases=["minigames", "mini", "games"])
    async def mini_game(self, ctx):
        pass


def setup(bot):
    bot.add_cog(LevelUpGames(bot))
