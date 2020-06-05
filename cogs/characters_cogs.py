import json
import random
import discord

from discord.ext import commands
from discord.ext import tasks

from realms.character import Character
from realms.user_characters import UserCharacters


NON_VOTE_ROLLS = 25
VOTE_ROLLS_MOD = +25


class Customisations(commands.Cog):
    with open(r"resources/archieve/waifus.json", "r") as file:
        RANDOM_CHARACTERS = json.load(file)
    random.shuffle(RANDOM_CHARACTERS)
    group = RANDOM_CHARACTERS[:5000]

    def __init__(self, bot):
        self.bot = bot
        self.cool_down_checks = {}

    @classmethod
    @tasks.loop(minutes=30)
    async def shuffle(cls):
        random.shuffle(cls.RANDOM_CHARACTERS)
        cls.group = cls.RANDOM_CHARACTERS[:5000]

    @commands.command(aliases=['c'])
    async def character(self, ctx):
        user_characters: UserCharacters = self.bot.cache.get('characters', ctx.author.id)
        if user_characters is None:
            user_characters = UserCharacters(user_id=ctx.author.id,
                                             database=self.bot.database,
                                             rolls=self.cool_down_checks.get('rolls_left', NON_VOTE_ROLLS),
                                             expires_in=self.cool_down_checks.get('expires_in', None))
            self.bot.cache.store('characters', ctx.author.id, user_characters)

        if not Checks.has_rolls(user_characters):
            if ctx.has_voted():
                return await ctx.send(f"<:HimeSad:676087829557936149> Oops! You dont have any more rolls left,"
                                      f" come back in {user_characters} hours when ive found some more characters!")
            else:
                return await ctx.send("<:HimeSad:676087829557936149> Oops! You dont have any more rolls left,"
                                      " upvote Crunchy to get more rolls and other awesome perks!\n"
                                      "https://top.gg/bot/656598065532239892/vote")

        c = random.choice(self.group)
        character_obj = Character(name=c['name'], icon=c['url'])
        embed = discord.Embed(
            title=character_obj.name,
            description=f"💪 **Power:** `{character_obj.power}`\n"
                        f"⚔️ **Attack:** `{character_obj.attack}`\n"
                        f"🛡️ **Defense:** `{character_obj.defense}`\n",
            color=self.bot.colour)
        print(character_obj.icon)
        embed.set_image(url=character_obj.icon)
        embed.set_footer(text=f"You have {user_characters.rolls_left} rolls left!")
        message = await ctx.send(embed=embed)
        user_characters.update_rolls()
        await self.submit_wait_for(message, character_obj)

    async def submit_wait_for(self, message: discord.Message, character_obj: Character):
        pass


class Checks:
    @classmethod
    def has_rolls(cls, user: UserCharacters):
        return user.rolls_left > 0




def setup(bot):
    bot.add_cog(Customisations(bot))


if __name__ == "__main__":
    test = Customisations("wow")
    print(random.choice(test.group))
