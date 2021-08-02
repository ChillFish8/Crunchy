from discord.ext import commands

from data.database import MongoDatabase


class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: MongoDatabase = self.bot.database

    @commands.is_owner()
    @commands.command(name="reload")
    async def reload_ext(self, ctx, command_name: str):
        try:
            if "chara" in command_name:
                query = "realms.cogs." + command_name
            else:
                query = "cogs." + command_name
            self.bot.reload_extension(query)
            await ctx.send("Reloaded module {}".format(query))
        except Exception as e:
            await ctx.send(str(e))


def setup(bot):
    bot.add_cog(OwnerCommands(bot))


if __name__ == "__main__":
    test = OwnerCommands("wow")
