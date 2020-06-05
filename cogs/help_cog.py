from discord.ext import commands
import discord

from utils.paginator import Paginator

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
        # "`manga` **-** Search for a Manga.", todo still needs scraping
    ]

    LIVE_COMMANDS = [
        "`addreleasechannel` **-** Get anime releases to a channel.",
        # "`todaysreleases` **-** Get today's anime releases.", todo work this out
        "`addnewschannel` **-** Get Crunchyroll payload to a channel.",
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
        "`removecharacter ` **-** Remove a collect character.",  # todo
    ]

    NSFW_COMMANDS = [
        "`hentai <tag - optional>` **-** Get some Hentai!",
        "`ass` **-** Lewd ass.",
        "`pussy` **-** Lewd pussy.",
        "`gonewild` **-** Title says it all.",
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    async def help(self, ctx, sub_sec: str = None):
        if sub_sec is not None:
            return await self.get_sub_page(ctx, sub_sec)
        else:
            embed1 = discord.Embed(description=f"Do `{ctx.prefix}help <command> for more info on each command`",
                                  color=self.bot.colour)
            embed1.set_author(name=f"{ctx.author.name} - Crunchy's Commands: | Page 1 / 2", icon_url=ctx.author.avatar_url)
            f1 = f"<:discord:642859572524220427>  **General Commands**  <:discord:642859572524220427>\n" \
                 f"" + "\n".join(self.GENERAL_COMMANDS)

            f2 = f"<:9887_ServerOwner:653722257356750889>  **Search Functions**  <:9887_ServerOwner:653722257356750889>\n" \
                 f"" + "\n".join(self.Search_COMMANDS)

            f3 = f"<:CrunchyRollLogo:676087821596885013>  **Live Feeds**  <:CrunchyRollLogo:676087821596885013>\n" \
                 f"" + "\n".join(self.LIVE_COMMANDS)
            embed1.add_field(name="\u200b", value=f1, inline=False)
            embed1.add_field(name="\u200b", value=f2, inline=False)
            embed1.add_field(name="\u200b", value=f3, inline=False)

            embed2 = discord.Embed(description=f"Do `{ctx.prefix}help <command> for more info on each command`",
                                   color=self.bot.colour)
            embed2.set_author(name=f"{ctx.author.name} - Crunchy's Commands: | Page 2 / 2", icon_url=ctx.author.avatar_url)

            f4 = f"<:gelati_cute:704784002355036190>  **Watch List Commands & Favourites**  <:gelati_cute:704784002355036190>\n" \
                 f"" + "\n".join(self.TRACKING_COMMANDS)

            f5 = f"<:HimeHappy:677852789074034691>  **Character Collection**  <:HimeHappy:677852789074034691>\n" \
                 f"" + "\n".join(self.CHARACTER_COMMANDS)

            embed2.add_field(name="\u200b", value=f4, inline=False)
            embed2.add_field(name="\u200b", value=f5, inline=False)

            if ctx.guild_config is not None:
                if ctx.guild_config.nsfw_enabled:
                    f6 = f"🔞  **NSFW**  🔞\n" \
                         f"" + "\n".join(self.NSFW_COMMANDS)
                    embed2.add_field(name="\u200b", value=f6, inline=False)
            else:
                f6 = f"🔞  **NSFW**  🔞\n" \
                     f"" + "\n".join(self.NSFW_COMMANDS)
                embed2.add_field(name="\u200b", value=f6, inline=False)
            embed1.set_footer(text="Part of the Crunchy the Crunchyroll Discord bot, Powered by CF8")
            embed2.set_footer(text="Part of the Crunchy the Crunchyroll Discord bot, Powered by CF8")
            pager = Paginator(embed_list=[embed1, embed2],
                              bot=self.bot,
                              message=ctx.message,
                              colour=self.bot.colour)
            return self.bot.loop.create_task(pager.start())

    async def get_sub_page(self, ctx, sub_sec):
        pass  # todo fill this

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))