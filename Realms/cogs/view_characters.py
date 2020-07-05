import discord

from discord.ext import commands

from realms.character import Character
from realms.user_characters import UserCharacters
from realms.static import Database

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
        self.bot: commands.Bot = bot

    @commands.command(name="view", aliases=['inspect', 'vc', 'viewcharacter'])
    async def character_details(self, ctx, *, character_name: str = None):
        if character_name is None:
            command = self.bot.get_command("viewcharacters")
            await ctx.send("<:HimeSad:676087829557936149> You didnt give me anyone to get. Check your list here:")
            return await command.invoke(ctx)

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
        # First Page  (General Details)
        embed = discord.Embed(color=self.bot.colour)
        embed.set_thumbnail(url=self.character.icon)
        embed.set_author(name=f"{self.character.name} - Level {self.character.level}",
                         icon_url=self.ctx.author.avatar_url)
        return embed

def setup(bot):
    bot.add_cog(ViewCharacters(bot))
