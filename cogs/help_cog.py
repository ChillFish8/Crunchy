import discord
import random

from discord.ext import commands
from utils.paginator import Paginator

RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]


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
        "`myfavourites` **-** Brings up your Favourite animes.",
        "`myqueue` **-** Brings up your current watchlist.",

        "`addanime` **-** Add an anime to your watchlist or favourites.",
        "`recommend` **-** Recommend an anime to a friend!",

        "`removewatchlist` **-** Delete something on your watchlist.",
        "`removerecommended` **-** Delete a recommendation on your list.",
        "`removefavourite` **-** Remove an anime from your favourites.",
    ]

    CONFIG_COMMANDS = [
        "`firewall` **-** Your recommended area between public and private.",
        # "`allow <user mention>` **-** Allow people to bypass the firewall command.",
        # "`block <user mention>` **-** Block people from adding and viewing your recommended.",
    ]

    CHARACTER_COMMANDS = [
        "`character ` **-** Get a random character, can you collect them all?",
        "`viewcharacters` **-** View all of your collected characters.",
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
        self.sub_help = SubEmbeds(bot.colour)

    @commands.command(aliases=['h'])
    async def help(self, ctx, sub_sec: str = None):
        if sub_sec is not None:
            return await self.get_sub_page(ctx, sub_sec)
        else:
            embed1 = discord.Embed(description=f"Do `{ctx.prefix}help <command> for more info on each command`",
                                   color=self.bot.colour)
            embed1.set_author(name=f"{ctx.author.name} - Crunchy's Commands: | Page 1 / 2",
                              icon_url=ctx.author.avatar_url)
            f1 = f"<:discord:642859572524220427>  **General Commands**  <:discord:642859572524220427>\n" \
                 f"" + "\n".join(self.GENERAL_COMMANDS)

            f4 = f"<:gelati_cute:704784002355036190>  **Watch List Commands & Favourites**  <:gelati_cute:704784002355036190>\n" \
                 f"" + "\n".join(self.TRACKING_COMMANDS)

            f3_2 = f"⚙️  **User config**  ⚙️\n" \
                   f"" + "\n".join(self.CONFIG_COMMANDS)
            embed1.add_field(name="\u200b", value=f1, inline=False)

            embed1.add_field(name="\u200b", value=f4, inline=False)
            embed1.add_field(name="\u200b", value=f3_2, inline=False)

            embed2 = discord.Embed(description=f"Do `{ctx.prefix}help <command> for more info on each command`",
                                   color=self.bot.colour)
            embed2.set_author(name=f"{ctx.author.name} - Crunchy's Commands: | Page 2 / 2",
                              icon_url=ctx.author.avatar_url)

            f2 = f"<:9887_ServerOwner:653722257356750889>  **Search Functions**  <:9887_ServerOwner:653722257356750889>\n" \
                 f"" + "\n".join(self.Search_COMMANDS)

            f3 = f"<:CrunchyRollLogo:676087821596885013>  **Live Feeds**  <:CrunchyRollLogo:676087821596885013>\n" \
                 f"" + "\n".join(self.LIVE_COMMANDS)

            f5 = f"<:HimeHappy:677852789074034691>  **Character Collection**  <:HimeHappy:677852789074034691>\n" \
                 f"" + "\n".join(self.CHARACTER_COMMANDS)

            embed2.add_field(name="\u200b", value=f3, inline=False)
            embed2.add_field(name="\u200b", value=f5, inline=False)
            embed2.add_field(name="\u200b", value=f2, inline=False)

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
        embed, url = self.sub_help.SUB_EMBED.get(sub_sec.lower(),
                                                 (
                                                     discord.Embed(description="This command has no sub help page.",
                                                                   color=self.bot.colour),
                                                     None)
                                                 )
        if embed is None:
            return await ctx.send(embed=embed)
        else:
            embed.set_footer(text="Part of the Crunchy the Crunchyroll Discord bot, Powered by CF8")
            embed.set_author(name=f"{ctx.author.name} - Sub Command | {sub_sec.capitalize()}",
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=random.choice(RANDOM_THUMBS))
            if url is not None:
                embed.set_image(url=url)
            return await ctx.send(embed=embed)


class SubEmbeds:
    def __init__(self, colour):
        self.SUB_EMBED = {
            'invite': (discord.Embed(description="This command give you a link to invite Crunchy to another server.",
                                     color=colour),
                       None),
            'vote': (discord.Embed(description="This command give you a link to vote for Crunchy to get awesome perks"
                                               " and support Crunchy in general!",
                                   color=colour),
                     None),
            'support': (
                discord.Embed(description="This command give you a link to join Crunchy's support server if you still"
                                          " need help or want to chat!",
                              color=colour),
                None),
            'serversettings': (
                discord.Embed(description="This will bring up a embed showing the config settings for Crunchy,"
                                          " for this guild.\n"
                                          "**Aliases:** `ss`",
                              color=colour),
                "https://cdn.discordapp.com/attachments/676092549248712704/718429619669303357/unknown.png"),
            'setprefix': (discord.Embed(description="This command will set a custom prefix.",
                                        color=colour),
                          None),
            'togglensfw': (
                discord.Embed(description="This command will enable or disable NSFW command for this server, "
                                          "when enabled Crunchy will *not* display NSFW commands or send any NSFW "
                                          "content regardless of if it is in a NSFW channel.",
                              color=colour),
                None),

            'myrecommended': (discord.Embed(description="This will show you a list with all the titles "
                                                        "( and urls if applicable) people have recommended you to "
                                                        "watch or read!\n"
                                                        "**Aliases:** `myr`, `recommended`",
                                            color=colour),
                              None),
            'myfavourites ': (discord.Embed(description="**Applies to both MyFavourites and MyQueue**\n"
                                                        "This will show you a list with all the titles "
                                                        "( and urls if applicable) that are in your list.\n"
                                                        "**Aliases:** `myf`, `favourites`",
                                            color=colour),
                              None),
            'myqueue ': (discord.Embed(description="**Applies to both MyFavourites and MyQueue**\n"
                                                   "This will show you a list with all the titles "
                                                   "( and urls if applicable) that are in your list.\n"
                                                   "**Aliases:** `myq`, `watchlist`",
                                       color=colour),
                         None),
            'addanime': (
                discord.Embed(description="This is how you add items to the command `watchlist` and `favourites`\n"
                                          "Example command:\n`-aa Tower of God "
                                          "url=https://www.crunchyroll.com/en-gb/tower-of-god`\n"
                                          "**Note - ** `url=` is a optional argument if you want "
                                          "Crunchy to hyper link the title."
                                          "**Aliases:** `aa`",
                              color=colour),
                None),
            'recommend': (discord.Embed(description="This is how you add items to someone's recommended list\n"
                                                    "Example command:\n`-aa @Crunchy Tower of God "
                                                    "url=https://www.crunchyroll.com/en-gb/tower-of-god`\n"
                                                    "**Note - ** `url=` is a optional argument if you want "
                                                    "Crunchy to hyper link the title."
                                                    "**Aliases:** `recc`",
                                        color=colour),
                          None),
            'removewatchlist': (discord.Embed(description="Use this command to remove a item from your list\n"
                                                          "Example command:\n`-rw 1` will remove the first item.\n"
                                                          "**Aliases:** `rw`",
                                              color=colour),
                                None),
            'removerecommended ': (discord.Embed(description="Use this command to remove a item from your list\n"
                                                             "Example command:\n`-rr 1` will remove the first item.\n"
                                                             "**Aliases:** `rr`",
                                                 color=colour),
                                   None),
            'removefavourite ': (discord.Embed(description="Use this command to remove a item from your list\n"
                                                           "Example command:\n`-rf 1` will remove the first item.\n"
                                                           "**Aliases:** `rf`",
                                               color=colour),
                                 None),
        }


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))
