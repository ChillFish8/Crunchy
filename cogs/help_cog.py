from discord.ext import commands
import discord

class HelpCog(commands.Cog):
    GENERAL_COMMANDS = [
        "`invite` **-** Invite me!",
        "`serversettings` **-** Get your server's current bot settings.",
        "`setprefix` **-** Set a custom prefix.",
        "`togglensfw` **-** Enable / Disable NSFW commands for this server.",
        "`vote` **-** Vote for me!",
        "`support` **-** Join our support server!",
    ]

    Search_COMMANDS = [
        "`animedetails` **-** Get details from Crunchyroll on an Anime.",
        "`manga` **-** Search for a Manga.",
    ]

    LIVE_COMMANDS = [
        "`addreleasechannel` **-** Get anime releases to a channel.",
        "`todaysreleases` **-** Get today's anime releases.",
        "`addnewschannel` **-** Get Crunchyroll news to a channel.",
    ]

    TRACKING_COMMANDS = [
        "`myrecommended` **-** View what animes people have recommended to you!",
        "`removerecommended` **-** Delete a recommendation on your list.",
        "`upnext` **-** Get the next anime in your watchlist.",
        "`myfavourites` **-** Brings up your Favourite animes.",
        "`recommend` **-** Recommend an anime to a friend!",
        "`toggle` **-** Toggle commands on/off (public and private).",
        "`myqueue` **-** Brings up your current watchlist.",
        "`addanime` **-** Add an anime to your watchlist or favourites.",
        "`removefavourite` **-** Remove an anime from your favourites.",
    ]

    CHARACTER_COMMANDS = [
        "`character ` **-** Get a random character, can you collect them all?",
        "`viewcharacter ` **-** View a collect character.",
        "`removecharacter ` **-** Remove a collect character.",
    ]

    NSFW_COMMANDS = [
        "`hentai` **-** ",
        "`ass` **-** ",
        "`neko` **-** ",
        "`pussy` **-** ",
        "`gonewild` **-** ",
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    async def help(self, ctx, sub_sec: str = None):
        if sub_sec is not None:
            return await self.get_sub_page(ctx, sub_sec)
        else:
            f1 = f"<:discord:642859572524220427>  **General Commands**  <:discord:642859572524220427>\n" \
                 f"" + "\n".join(self.GENERAL_COMMANDS)

            f2 = f"<:9887_ServerOwner:653722257356750889>  **Search Functions**  <:9887_ServerOwner:653722257356750889>\n" \
                 f"" + "\n".join(self.Search_COMMANDS)

            f3 = f"<:CrunchyRollLogo:676087821596885013>  **Live Feeds**  <:CrunchyRollLogo:676087821596885013>\n" \
                 f"" + "\n".join(self.LIVE_COMMANDS)

            f4 = f"<:gelati_cute:704784002355036190>  **Watch List Commands & Favourites**  <:gelati_cute:704784002355036190>\n" \
                 f"" + "\n".join(self.TRACKING_COMMANDS)

            f5 = f"<:HimeHappy:677852789074034691>  **Character Collection**  <:HimeHappy:677852789074034691>\n" \
                 f"" + "\n".join(self.CHARACTER_COMMANDS)

            embed = discord.Embed(description=f"Do `{ctx.prefix}help <command> for more info on each command`",
                                  color=self.bot.colour)
            embed.set_author(name=f"{ctx.author.name} - Crunchy's Commands:", icon_url=ctx.author.avatar_url)

            embed.add_field(name="\u200b", value=f1, inline=False)
            embed.add_field(name="\u200b", value=f2, inline=False)
            embed.add_field(name="\u200b", value=f3, inline=False)
            embed.add_field(name="\u200b", value=f4, inline=False)
            embed.add_field(name="\u200b", value=f5, inline=False)

            if ctx.guild_config is not None:
                if ctx.guild_config.nsfw_enabled:
                    f6 = f"🔞  **NSFW**  🔞\n" \
                         f"" + "\n".join(self.NSFW_COMMANDS)
                    embed.add_field(name="\u200b", value=f6, inline=False)
            else:
                f6 = f"🔞  **NSFW**  🔞\n" \
                     f"" + "\n".join(self.NSFW_COMMANDS)
                embed.add_field(name="\u200b", value=f6, inline=False)
            embed.set_footer(text="Part of the Crunchy the Crunchyroll Discord bot, Powered by CF8")
            return await ctx.send(embed=embed)

    async def get_sub_page(self, ctx, sub_sec):
        pass  # todo fill this

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))