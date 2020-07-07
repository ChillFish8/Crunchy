import discord
import time

from datetime import datetime, timedelta
from discord.ext import commands, tasks

from realms.generation.monsters import MonsterManual
from realms.static import Database
from realms.user_characters import UserCharacters

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


class LevelUpGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monster_manual = MonsterManual()
        self._encounters = {}

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

    @commands.command(name="encounter")
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
        contents = await self.monster_manual.get_random_monster(4)
        await ctx.send(contents)


def setup(bot):
    bot.add_cog(LevelUpGames(bot))
