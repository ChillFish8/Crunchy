from discord.ext import commands

from database.database import GuildConfig

class Customisations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['setprefix'])
    async def set_prefix(self, ctx, *, prefix: str):
        """ Set a new prefix """
        config: GuildConfig = ctx.guild_config
        config.set_prefix(prefix)
        self.bot.cache.store('guilds', ctx.guild.id, config)
        await ctx.send(f"<:HimeHappy:677852789074034691> My prefix is now `{config.prefix}`")

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(aliases=['resetprefix'])
    async def reset_prefix(self, ctx):
        """ If you wanna go back to default """
        config: GuildConfig = ctx.config
        new = config.reset_prefix()
        self.bot.cache.store('guilds', ctx.guild.id, config)
        await ctx.send(f"<:HimeHappy:677852789074034691> My prefix is now back to `{new}` **(default)**")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['togglensfw'])
    async def toggle_nsfw(self, ctx):
        """ Set a new prefix """
        config: GuildConfig = ctx.guild_config
        new = config.toggle_nsfw()
        self.bot.cache.store('guilds', ctx.guild.id, config)
        await ctx.send(f"<:HimeHappy:677852789074034691> NSFW is now {'enabled.' if new else 'disabled.'}")

    async def cog_command_error(self, ctx, error):
        """ We catch out own error locally to keep it simple """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "<:HimeSad:676087829557936149> Sorry! Your dont seem to have the permission `ADMINISTRATOR`"
                " Please make sure you have this permission before using this command.")

def setup(bot):
    bot.add_cog(Customisations(bot))