import discord
import time

from discord.ext import commands, tasks

from realms.static import Database
from realms.user_characters import UserCharacters
from realms.parties import Party
from realms.encounter import Encounter

HIME_MAD = "https://cdn.discordapp.com/emojis/676087826827444227.png?v=1"
HIME_SAD = "https://cdn.discordapp.com/emojis/676087829557936149.png?v=1"
LIMIT = 4


def format_time(time_stamp: float):
    current = time.time()
    delta = time_stamp - current

    minutes, secs = divmod(delta, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(minutes, 24)
    if days:
        return f"{days}d, {hours}h, {minutes}m, {secs}s."
    else:
        return f"{hours}h, {minutes}m, {secs}s."


class PartialCommand:
    def __init__(self, command, *args):
        self.name = command
        self.args = args


class LevelUpGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._encounters = {}
        self._pending_accepts = {}
        self._pending_interactions = {}

    @tasks.loop(seconds=30)
    async def clear_outdated(self):
        for user, item in self._encounters.items():
            ts = item.get('timestamp')
            if ts is not None:
                if ts <= time.time():
                    del self._encounters[user]

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        data['user'] = int(data['user'])
        if self._encounters.get(data['user']):
            if self._encounters.get(data['user'])['uses'] >= LIMIT:
                del self._encounters[data['user']]
            else:
                self._encounters.get(data['user'])['uses'] -= LIMIT
        else:
            self._encounters[data['user']] = {
                'uses': -LIMIT
            }

    @commands.command()
    @commands.is_owner()
    async def fudge_vote(self, ctx):
        await self.on_dbl_vote({"user": str(ctx.author.id)})

    @commands.command(name="acceptquest", aliases=['quest', 'accept'])
    async def accept_quest(self, ctx, *args):
        if self._pending_accepts.get(ctx.author.id):
            if len(args) == 0:
                return await ctx.send("<:HimeSad:676087829557936149> That's not a valid quest! "
                                      "They must be the number representing the quest!")
            else:
                context = self._pending_accepts[ctx.author.id]
                if ctx.channel.id == context.channel.id:
                    try:
                        quest_no = int(args[0])
                        if quest_no in range(1, 5):
                            del self._pending_accepts[ctx.author.id]
                            self.bot.dispatch('quest_accept', quest_no, context.author)
                        else:
                            return await ctx.send("<:HimeSad:676087829557936149> That's not a valid quest! "
                                                  "They must be the number representing the quest!")
                    except ValueError:
                        return await ctx.send("<:HimeSad:676087829557936149> That's not a valid quest! "
                                              "They must be the number representing the quest!")

    @commands.command(name="stack")
    async def stack_cards(self, ctx, card_id: int=0, card_amount: int=0):
        if not self._pending_interactions.get(ctx.author.id):
            return await ctx.send("<:HimeSad:676087829557936149> You dont have a active encounter session running!")
        else:
            del self._pending_interactions[ctx.author.id]
        if 0 <= card_id > 5:
            return await ctx.send("<:HimeSad:676087829557936149> You have to give me a card number between 1-5"
                                  f" Example command: `{ctx.prefix}stack 1 2`")

        if 0 <= card_amount > 5:
            return await ctx.send("<:HimeSad:676087829557936149> You have to give me a amount of cards between 1-5"
                                  f" Example command: `{ctx.prefix}stack 1 2`")

        temp = PartialCommand('stack', card_id, card_amount)
        self.bot.dispatch('encounter_command', temp, ctx.author)

    @stack_cards.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f"Oops! That isn't a valid input, try: `{ctx.prefix}stack 1 2`.")

    @commands.command()
    async def attack(self, ctx):
        if not self._pending_interactions.get(ctx.author.id):
            return await ctx.send("<:HimeSad:676087829557936149> You dont have a active encounter session running!")
        else:
            del self._pending_interactions[ctx.author.id]

        temp = PartialCommand('attack')
        self.bot.dispatch('encounter_command', temp, ctx.author)

    def submit_callback(self, ctx: commands.Context, interaction=False):
        if interaction:
            self._pending_interactions[ctx.author.id] = ctx
        else:
            self._pending_accepts[ctx.author.id] = ctx

    @commands.command()
    async def encounter(self, ctx):
        if self._encounters.get(ctx.author.id):
            if self._encounters.get(ctx.author.id)['uses'] >= LIMIT:
                if not ctx.has_voted(user_id=ctx.author.id):
                    embed = discord.Embed(title="Slow down adventurer!", color=self.bot.colour)
                    embed.set_thumbnail(url=HIME_MAD)
                    embed.description = "I dont have an unlimited stock " \
                                        "of monsters just to give to you! If you [vote for me here]" \
                                        "(https://top.gg/bot/656598065532239892) you might just persuade me to let " \
                                        "you back in the dungeon for another round of kicking butt!"
                    embed.set_footer(text="Voting helps support the development of Crunchy.")
                    return await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Slow down adventurer!", color=self.bot.colour)
                    embed.set_thumbnail(url=HIME_SAD)
                    embed.description = "I can't believe you cleared all those monsters so quickly!\n" \
                                        f"You'll have to come back in " \
                                        f"{format_time(self._encounters.get(ctx.author.id)['timestamp'])}"
                    embed.set_footer(text="Voting helps support the development of Crunchy.")
                    return await ctx.send(embed=embed)

        user_area = UserCharacters(ctx.author.id, Database.db)
        party = Party(self.bot, ctx, user_area=user_area)
        encounter = Encounter(self.bot, ctx, party, self.submit_callback, user_area)
        return await encounter.menu()


def setup(bot):
    bot.add_cog(LevelUpGames(bot))
