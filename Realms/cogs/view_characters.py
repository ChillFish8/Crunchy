import discord

from discord.ext import commands

from realms.character import Character
from realms.user_characters import UserCharacters
from realms.static import Database
from utils.paginator import Paginator

NON_VOTE_ROLLS = 15
VOTE_ROLLS_MOD = +25
RANDOM_EMOJIS = ['💞', '💗', '💖', '💓']


HAPPY_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png",
    "https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png"
]
SAD_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784461391167568/sad.png",
]


class ViewCharacters(commands.Cog):
    database = Database.db

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ViewCharacters(bot))
