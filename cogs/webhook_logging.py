import json

from discord.ext import commands


with open("config.json") as file:
    config = json.load(file)


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.GUILD_URL = config.get("guild_webhook")
        self.VOTE_URL = config.get("vote_webhook")
        self.COMMAND_URL = config.get("command_webhook")
        self.guild_webhook = None
        self.vote_webhook = None
        self.command_webhook = None

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if self.guild_webhook is None:
            return
        desc = "💜"
        if len(guild.members) > 1000:
            desc += "🔥"
        if len(guild.members) > 10000:
            desc += "🌟"
        desc += " " + f"Joined guild {guild}, Total members: {len(guild.members)}"
        await self.guild_webhook.send(content=desc)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if self.guild_webhook is None:
            return
        desc = "💔"
        if len(guild.members) > 1000:
            desc += "💔"
        if len(guild.members) > 10000:
            desc += "💔"
        desc += " " + f"Lost guild {guild}, Total members: {len(guild.members)}"
        await self.guild_webhook.send(content=desc)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if self.command_webhook is None:
            return
        desc = f"**User:** `{ctx.author.id}` **|** " \
               f"**Guild:** `{ctx.guild.id if ctx.guild is not None else 'direct message'}` **|** " \
               f"**Command:** `{ctx.command}`"
        await self.command_webhook.send(content=desc)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        if self.vote_webhook is None:
            return
        await self.vote_webhook.send(
            f"**New Upvote**  |  User: `{data['user']}`")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        if self.vote_webhook is None:
            return
        await self.vote_webhook.send(
            f"**New Upvote**  |  User: `{data['user']}`")

def setup(bot):
    bot.add_cog(Search(bot))