import dbl
import json
import time

from datetime import timedelta
from discord.ext import commands, tasks
from colorama import Fore

from logger import Logger

with open("config.json") as file:
    config = json.load(file)


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = config.get('dbl_token')
        self.dblpy = dbl.DBLClient(self.bot, self.token,
                                   webhook_path='/dblwebhook',
                                   webhook_auth=config.get("dbl_password"),
                                   webhook_port=config.get("dbl_port"))
        self.update_stats.start()
        self.clear_votes.start()

    @tasks.loop(minutes=10)
    async def clear_votes(self):
        timestamp = time.time()
        removed = self.bot.database.remove_outdated(time_secs=timestamp)
        Logger.log_dbl("Removed: {} outdated votes".format(removed))

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        try:
            await self.dblpy.post_guild_count()
            Logger.log_dbl('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            Logger.log_dbl(Fore.RED + 'Failed to post server count\n{}: {}'.format(type(e).__name__, e), error=True)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        data['user'] = int(data['user'])
        now = time.time()
        expires = now + timedelta(hours=24).total_seconds()
        check = self.bot.database.get_vote(user_id=data['user'])
        if check is None:
            self.bot.database.add_vote(data['user'], expires)
            self.bot.cache.store('votes', data['user'], {'user_id': data['user'], 'expires_in': expires})
        else:
            self.bot.database.update_vote(data['user'], expires)
            self.bot.cache.store('votes', data['user'], {'user_id': data['user'], 'expires_in': expires})

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        data['user'] = int(data['user'])
        now = time.time()
        expires = now + timedelta(hours=24).total_seconds()
        check = self.bot.database.get_vote(user_id=data['user'])
        if check is None:
            self.bot.database.add_vote(data['user'], expires)
            self.bot.cache.store('votes', data['user'], {'user_id': data['user'], 'expires_in': expires})
        else:
            self.bot.database.update_vote(data['user'], expires)
            self.bot.cache.store('votes', data['user'], {'user_id': data['user'], 'expires_in': expires})


def setup(bot):
    bot.add_cog(TopGG(bot))