import json
import random

from discord.ext import commands
from discord.ext import tasks

# from realms.character import Character
from realms.user_characters import UserCharacters

class Customisations(commands.Cog):
    with open(r"../resources/archieve/waifus.json", "r") as file:
        RANDOM_CHARACTERS = json.load(file)
    random.shuffle(RANDOM_CHARACTERS)
    group = RANDOM_CHARACTERS[:5000]

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    @tasks.loop(minutes=30)
    async def shuffle(cls):
        random.shuffle(cls.RANDOM_CHARACTERS)
        cls.group = cls.RANDOM_CHARACTERS[:5000]

    @commands.command(aliases=['c'])
    async def character(self, ctx):


class Checks:
    @classmethod
    async def has_rolls(cls, user: UserCharacters):




def setup(bot):
    bot.add_cog(Customisations(bot))


if __name__ == "__main__":
    test = Customisations("wow")
    print(random.choice(test.group))
