from discord.ext import commands
import discord


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['v'])
    async def vote(self, ctx):
        """ Set a new prefix """
        await ctx.send(f"Vote for me here to get some awesome perks!"
                       f" https://top.gg/bot/656598065532239892/vote")

    @commands.command()
    async def support(self, ctx):
        """ If you wanna go back to default """
        await ctx.send(f"You can join my support server here: https://discord.gg/tJmEzWM")

    @commands.guild_only()
    @commands.command(aliases=['ss', 'serversettings'])
    async def server_settings(self, ctx):
        """ Set a new prefix """
        embed = discord.Embed(
            description=f"__**Server Info**__\n"
                        f"Name: `{ctx.guild}`\n"
                        f"Guild Id: `{ctx.guild.id}`\n\n"
                        f"__**Server Settings**__\n"
                        f"Prefix: `{ctx.prefix}`\n"
                        f"Premium: `{ctx.guild_config.premium}`\n"
                        f"NSFW: `{ctx.guild_config.nsfw_enabled}`\n",
            color=self.bot.colour
        )
        embed.set_author(name=f"{ctx.guild.name}'s Server Settings:", icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/675647130647658527/61515ba4de15b"
                "723324b5d7cb8754ed1.webp?size=1024")
        embed.set_footer(text="Part of Crunchy, The Crunchyroll Discord bot. Powered by CF8")
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GeneralCommands(bot))