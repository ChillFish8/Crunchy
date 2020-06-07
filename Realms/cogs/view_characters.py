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
from realms.hints import hinter

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

    @commands.command(name="view", aliases=['inspect'])
    async def character_details(self, ctx, *, character_name: str = None):
        if character_name is None:
            return await ctx.send("<:HimeSad:676087829557936149> You haven't specified a character to inspect")

        user_area = UserCharacters(user_id=ctx.author.id, database=self.database)
        character_dict = user_area.get_character(search=character_name)
        if character_dict is None:
            return await ctx.send("<:HimeSad:676087829557936149> Sorry! >_< I couldn't find that character "
                                  "in your area, Time to get rolling and collecting more!")

        character = Character().from_dict(character_dict)
        details = Display(self.bot, character, ctx)
        await ctx.send(embed=details.generate_pages())
        user_area.update_character(character)

    async def cog_command_error(self, ctx, error):
        raise error


class Display:
    def __init__(self, bot, character: Character, ctx):
        self.ctx = ctx
        self.bot = bot
        self.character = character

    def generate_pages(self):
        page_list = []

        # First Page  (General Details)
        embed = discord.Embed(color=self.bot.colour)
        embed.set_thumbnail(url=self.character.icon)
        embed.set_author(name=f"{self.character.name} - General Info", icon_url=self.ctx.author.avatar_url)
        embed.set_footer(text=hinter.get_hint())
        delta = time.gmtime(self.character.last_active)
        embed.description = f"{self.character.get_emotion()}\n**Last active:** " \
                            f"`{delta.tm_mday}/{delta.tm_mon}/{delta.tm_year} " \
                            f"{delta.tm_hour}:{delta.tm_min}:{delta.tm_sec}` GMT\n"
        embed.add_field(
            name="\u200b",
            value=f"**__Base Stats__**\n"
                  f"💪 **Power:** `{self.character.power}`\n\n"
                  f"⚔️ **Attack:** `{self.character.attack}`\n\n"
                  f"🛡️ **Defense:** `{self.character.defense}`\n",
            inline=True)
        embed.add_field(
            name="\u200b",
            value=f"**__Character Stats__**\n"
                  f"{self.character.render_character_info()}",
            inline=True)
        embed.add_field(
            name="\u200b",
            value=f"**__Modifiers__**\n"
                  f"{self.character.render_modifiers()}",
            inline=False)
        return embed

def setup(bot):
    bot.add_cog(ViewCharacters(bot))
