import random
import discord
import asyncio
import json
import typing

from collections import deque
from discord.ext import commands
from datetime import datetime

from data.user_content import UserFavourites, UserRecommended, UserWatchlist
from utils.paginator import Paginator

with open("command_settings.json", "r") as file:
    COMMAND_SETTINGS = json.load(file)

FALSE_PREMIUM_MAX_IN_STORE = COMMAND_SETTINGS.get("nopremium_max_per_storage")
TRUE_PREMIUM_MAX_IN_STORE = COMMAND_SETTINGS.get("premium_max_per_storage")
PREMIUM_URL = COMMAND_SETTINGS.get("premium_url")

HAPPY_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png",
    "https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png"
]
SAD_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784461391167568/sad.png",
]
RANDOM_EMOJIS = [
    '<:cheeky:717784139226546297>',
    '<:HimeHappy:677852789074034691>',
    '<:ok:717784139943641088>',
    '<:thank_you:717784142053507082>',
    '<:exitment:717784139641651211>',
]


async def add_watchlist(ctx, bot, name, url):
    user_tracker: UserWatchlist = UserWatchlist(user_id=ctx.author.id, database=bot.database)
    if (user_tracker.amount_of_items >= FALSE_PREMIUM_MAX_IN_STORE) and (
            ctx.has_voted(ctx.author.id) == 0):
        return {'content': "<:HimeMad:676087826827444227> Oh no! "
                           "You dont have enough space in your watchlist "
                           "to add this, get more storage by voting here "
                           "https://top.gg/bot/656598065532239892/vote"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[0]) and (
            ctx.has_voted(ctx.author.id) == 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh no! "
                           f"You seem to have maxed out your watchlist, you can get more by"
                           f" buying premium here to help support my development: {PREMIUM_URL}"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[1]) and (
            ctx.has_voted(ctx.author.id) > 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh wow! "
                           f"You've managed to add over {TRUE_PREMIUM_MAX_IN_STORE[1]} things to your watchlist area! "
                           f"However, you'll need to either delete some to add more or contact my developer"
                           f" you can find him here: https://discord.gg/tJmEzWM"
                }
    else:
        try:
            user_tracker.add_content({'name': name, 'url': url})
            return {
                'content': f"<:HimeHappy:677852789074034691> Success!"
                           f" I've added {name} to your watchlist!"
            }
        except (ValueError, TypeError, IndexError):
            return False


async def add_favourites(ctx, bot, name, url):
    user_tracker: UserFavourites = UserFavourites(user_id=ctx.author.id, database=bot.database)
    if (user_tracker.amount_of_items >= FALSE_PREMIUM_MAX_IN_STORE) and (
            ctx.has_voted(ctx.author.id) == 0):
        return {'content': "<:HimeMad:676087826827444227> Oh no! "
                           "You dont have enough space in your favourites "
                           "to add this, get more storage by voting here "
                           "https://top.gg/bot/656598065532239892/vote"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[0]) and (
            ctx.has_voted(ctx.author.id) == 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh no! "
                           f"You seem to have maxed out your favourites, you can get more by"
                           f" buying premium here to help support my development: {PREMIUM_URL}"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[1]) and (
            ctx.has_voted(ctx.author.id) > 1):
        return {
            'content': f"<:HimeMad:676087826827444227> Oh wow! "
                       f"You've managed to add over {TRUE_PREMIUM_MAX_IN_STORE[1]} things to "
                       f"your favourites area! "
                       f"However, you'll need to either delete some to add more or "
                       f"contact my developer"
                       f" you can find him here: https://discord.gg/tJmEzWM"
        }
    else:
        try:
            user_tracker.add_content({'name': name, 'url': url})
            return {
                'content': f"<:HimeHappy:677852789074034691> Success!"
                           f" I've added {name} to your favourites!"
            }
        except (ValueError, TypeError, IndexError):
            return False


async def add_both(*args, **kwargs):
    return (await add_favourites(*args, **kwargs)), (await add_watchlist(*args, **kwargs))


class AddingAnime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.options = {0: add_favourites, 1: add_watchlist, 2: add_both}

    @commands.command(aliases=['aa', 'addanime'])
    async def add_anime(self, ctx, *, argument: str):
        """ Add Anime to a collection """
        items = argument.split("url=", 1)
        if len(items) > 1:
            name, url = items
            if name == '':
                split = url.split(" ", 1)
                if len(split) > 1:  # Reverse the order in case someone is a moron
                    name, url = split[1], split[0]
                else:
                    return await ctx.send(f"<:HimeMad:676087826827444227> Oops! "
                                          f"You didnt give a title but gave a url, "
                                          f"please do `{ctx.prefix}help addanime` for more info.")
            if not url.startswith("http"):
                url = None
        else:
            name, url = items[0], None
        if name.endswith(" "):
            name = name[:len(name) - 1]

        desc = f"Where would you like the Anime to go?\n" \
               f"Click on the Emoji related to the choice you want to make!\n\n" \
               f"💖 **- Add to Favourites**\n\n" \
               f"<:CrunchyRollLogo:676087821596885013> **- Add to watchlist**\n\n" \
               f"<:9887_ServerOwner:653722257356750889> **- Add to both lists**\n\n"

        embed = discord.Embed(
            title="What list should I add it to?",
            description=desc,
            color=self.bot.colour
        )

        message: discord.Message = await ctx.send(embed=embed)
        BASE_EMOJIS = [
            "💖", "<:CrunchyRollLogo:676087821596885013>", "<:9887_ServerOwner:653722257356750889>"
        ]
        for emoji in BASE_EMOJIS:
            await message.add_reaction(emoji)

        def check(r: discord.Reaction, u: discord.User):
            return (str(r.emoji) in BASE_EMOJIS) and (u.id == ctx.author.id) and (
                    r.message.id == message.id)

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.delete()
            return await ctx.send(content="The selection period has expired.")

        results = await self.options[BASE_EMOJIS.index(str(reaction.emoji))](ctx, self.bot, name,
                                                                             url)
        if not isinstance(results, tuple):
            if not results:
                await message.delete()
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to "
                    "your list!")
            else:
                await message.delete()
                return await ctx.send(**results)
        else:
            if not results[0] or not results[1]:
                await message.delete()
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to "
                    "your list!")
            else:
                for res in results:
                    if not res['content'].startswith("<:HimeHappy:677852789074034691>"):
                        return await ctx.send(**res)
                else:
                    await message.delete()
                    return await ctx.send(
                        f"<:HimeHappy:677852789074034691> Success!"
                        f""" I've added "{name}" to both your watchlist and favourites!"""
                    )

    @commands.command(aliases=['recc', 'rec', 'reccomend', 'reccommend'])
    async def recommend(self, ctx, user: discord.Member = None, *, argument: str = None):
        """ Add Anime to to someone's recommended list """
        if user is None:
            return await ctx.send(
                f"<:HimeMad:676087826827444227> Oops! "
                f"You didnt mention the person you wanted to recommend an Anime to."
            )

        user_area = UserRecommended(user_id=user.id, database=self.bot.database)
        if not user_area.is_public:
            return await ctx.send(
                f"<:HimeMad:676087826827444227> Oops! "
                f"The user you mentioned has their recommended list set to private."
            )

        if argument is None:
            return await ctx.send(
                f"<:HimeMad:676087826827444227> Oh no! "
                f"You didnt give me anything to add to {user.display_name}'s recommended list."
                f" Do `{ctx.prefix}help recommended` for more info."
            )

        items = argument.split("url=", 1)
        if len(items) > 1:
            name, url = items
            if name == '':
                split = url.split(" ", 1)
                if len(split) > 1:  # Reverse the order in case someone is a moron
                    name, url = split[1], split[0]
                else:
                    return await ctx.send(
                        f"<:HimeMad:676087826827444227> Oops! "
                        f"You didnt give a title but gave a url, "
                        f"please do `{ctx.prefix}help addanime` for more info."
                    )
            if not url.startswith("http"):
                url = None
        else:
            name, url = items[0], None
        if name.endswith(" "):
            name = name[:len(name) - 1]
        try:
            user_area.add_content({'name': name, 'url': url})
            return await ctx.send(f"<:HimeHappy:677852789074034691> Success!"
                                  f""" I've added "{name}" to {user.name}'s recommended list.""")
        except Exception as e:
            return await ctx.send(f"Oh no! A error jumped out and scared me: {e}")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> You need to give the title of the item at least "
                "for this command.")


class UserSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def allow(self, ctx, user: discord.Member):
    #    """ Allow a user to bypass the public/private system """
    #    if ctx.author.id == user.id:
    #        return await ctx.send(
    #           f"<:HimeMad:676087826827444227> You can't whitelist yourself silly!")
    #    user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
    #    user_area.bypass(user.id)
    #    return await ctx.send(f"<:HimeHappy:677852789074034691> User {user.name} is now"
    #                          f" whitelisted for your area.")

    # @commands.command(aliases=['block'])
    # async def disallow(self, ctx, user: discord.Member):
    #    """ Disallow a user to bypass the public/private system """
    #    if ctx.author.id == user.id:
    #        return await ctx.send(f"<:HimeMad:676087826827444227> You can't block yourself silly!")
    #    user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
    #    user_area.block(user.id)
    #    return await ctx.send(f"<:HimeHappy:677852789074034691> User {user.name} is now"
    #                          f" blocked from your area.")

    @commands.command(aliases=['fw'])
    async def firewall(self, ctx, command_: str):
        """ Toggle public/private system """
        if command_ == "recommended":
            user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
            mode = user_area.toggle_public()
            return await ctx.send(f"<:HimeHappy:677852789074034691> Your recommended"
                                  f" list is now {'**public**' if mode else '**private**'}")
        elif command_ == "watchlist":
            user_area = UserWatchlist(user_id=ctx.author.id, database=self.bot.database)
            mode = user_area.toggle_public()
            return await ctx.send(f"<:HimeHappy:677852789074034691> Your watchlist"
                                  f" list is now {'**public**' if mode else '**private**'}")
        elif command_ == "favourites":
            user_area = UserFavourites(user_id=ctx.author.id, database=self.bot.database)
            mode = user_area.toggle_public()
            return await ctx.send(f"<:HimeHappy:677852789074034691> Your favourites"
                                  f" list is now {'**public**' if mode else '**private**'}")
        else:
            return await ctx.send(f"Sorry, that's not a valid command to firewall.")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> You need to specify the command"
                " (`recommended`, `watchlist`, `favourites`)"
                " or give me a channel Id for this command.")


async def convert_member(ctx: commands.Context, member_str: str):
    converter = commands.MemberConverter()
    return await converter.convert(ctx, member_str)


class ViewTracked(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_embeds(self, user: discord.User, area):
        pages, rem = divmod(area.amount_of_items, 5)
        if rem != 0:
            pages += 1

        embeds = []
        for i, chunk in enumerate(area.get_blocks()):
            embed = discord.Embed(color=self.bot.colour, timestamp=datetime.now()) \
                .set_footer(text=f"Page {i + 1} / {pages}")
            for x, item in enumerate(chunk):
                if item['url'] is not None:
                    embed.add_field(
                        value=f"** {x + i * 5 + 1} ) - [{item['name']}]({item['url']})**",
                        name="\u200b",
                        inline=False)
                else:
                    embed.add_field(value=f"** {x + i * 5 + 1} ) - {item['name']}**",
                                    name="\u200b",
                                    inline=False)
            embed.set_thumbnail(url=random.choice(HAPPY_URL))
            embed.set_author(name=f"{user.name}'s {area.type}", icon_url=user.avatar_url)
            embeds.append(embed)
        return embeds

    async def cycle_items(
            self,
            ctx: commands.Context,
            items: typing.Union[UserWatchlist, UserFavourites, UserRecommended],
    ):
        title = f"{ctx.author.name}'s"
        if isinstance(items, UserWatchlist):
            title += " watchlist"
        elif isinstance(items, UserFavourites):
            title += " favourites"
        elif isinstance(items, UserRecommended):
            title += " recommended"
        else:
            raise TypeError(f"No corresponding message for type: {items!r}")

        pages = []
        for item in items.contents:
            embed = discord.Embed(color=self.bot.colour, title=f"Name - {item['name']}")
            embed.set_author(name=title, icon_url=ctx.author.avatar_url)
            embed.url = item['url']
            embed.description = "React with the \🔍 icon to search for details\n"
            pages.append((embed, item))

        pages = deque(pages)

        current = pages[0]
        msg = await ctx.send(embed=current[0])

        emojis = ("◀️", "🔍", "▶️")
        try:
            for reaction in emojis:
                await msg.add_reaction(reaction)
        except discord.Forbidden:
            return await ctx.send("Oops! Im missing the permission to add reactions.")

        def check(r: discord.Reaction, u: discord.User):
            return (
                    str(r.emoji) in emojis
                    and u.id == ctx.author.id
                    and r.message.id == msg.id
            )

        while True:
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30, check=check)
                reaction = str(reaction.emoji)
            except asyncio.TimeoutError:
                break

            if reaction not in emojis:
                print("not in?")
                continue

            if reaction == emojis[0]:  # left shift
                pages.rotate(-1)
            elif reaction == emojis[2]:  # right shift
                pages.rotate(1)
            elif reaction == emojis[1]:  # search
                command: commands.Command = self.bot.get_command("animedetails")
                try:
                    await msg.delete()
                except discord.Forbidden:
                    return
                return await command(ctx, *current[1]['name'].split(" "))

            current = pages[0]
            await msg.edit(embed=current[0])

    @commands.command(aliases=['myw', 'watchlist', "mywatchlist"])
    async def my_watchlist(self, ctx, option=None):
        """
        Get your or someone else's watch list,

        args:
            option - This can be any string but can only be valid as a bool
                     or a member to be used by the member converter but not Both.
                     In this case Member will always be picked over the cycle option.


        """

        cycle = False
        member = None

        if option is not None:
            cycle = option.lower() == "--cycle" or option.lower() == "-c"

            try:
                member = await convert_member(ctx, option)
            except commands.BadArgument:
                member = None

        if cycle:
            user_area = UserWatchlist(user_id=ctx.author.id, database=self.bot.database)
            if user_area.amount_of_items <= 0:
                embed = discord.Embed(color=self.bot.colour)
                embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                    f"have anything in {'your' if member is None else 'their'} " \
                                    f"watchlist,\n lets get filling it!"
                embed.set_thumbnail(url=random.choice(SAD_URL))
                embed.set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
                embed.set_author(
                    name=f"{ctx.author.name}'s {user_area.type}",
                    icon_url=ctx.author.avatar_url
                )
                return await ctx.send(embed=embed)

            return await self.cycle_items(ctx, user_area)

        if member is not None:
            user_ = member
            user_area = UserWatchlist(user_id=member.id, database=self.bot.database)
            if not user_area.is_public:
                return await ctx.send("Oops! This user has their watchlist firewalled (Private).")
        else:
            user_ = ctx.author
            user_area = UserWatchlist(user_id=ctx.author.id, database=self.bot.database)

        if user_area.amount_of_items <= 0:
            embed = discord.Embed(color=self.bot.colour) \
                .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
            embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                f"have anything in {'your' if member is None else 'their'} " \
                                f"watchlist,\n lets get filling it!"
            embed.set_thumbnail(url=random.choice(SAD_URL))
            embed.set_author(name=f"{user_.name}'s {user_area.type}", icon_url=user_.avatar_url)
            return await ctx.send(embed=embed)
        else:
            embeds = await self.generate_embeds(user=user_, area=user_area)
            if len(embeds) > 1:
                pager = Paginator(embed_list=embeds,
                                  bot=self.bot,
                                  message=ctx.message,
                                  colour=self.bot.colour)
                return self.bot.loop.create_task(pager.start())
            return await ctx.send(embed=embeds[0])

    @commands.command(aliases=['myf', 'favourites', 'myfavourites'])
    async def my_favourites(self, ctx, option=None):
        """ Get your or someone else's favourites list
            args:
                option - This can be any string but can only be valid as a bool
                         or a member to be used by the member converter but not Both.
                         In this case Member will always be picked over the cycle option.
        """

        cycle = False
        member = None

        if option is not None:
            cycle = option.lower() == "--cycle" or option.lower() == "-c"

            try:
                member = await convert_member(ctx, option)
            except commands.BadArgument:
                member = None

        if cycle:
            user_area = UserFavourites(user_id=ctx.author.id, database=self.bot.database)
            if user_area.amount_of_items <= 0:
                embed = discord.Embed(color=self.bot.colour) \
                    .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
                embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                    f"have anything in {'your' if member is None else 'their'} favourites,\n" \
                                    f" lets get filling it!"
                embed.set_thumbnail(url=random.choice(SAD_URL))
                embed.set_author(
                    name=f"{ctx.author.name}'s {user_area.type}",
                    icon_url=ctx.author.avatar_url
                )
                return await ctx.send(embed=embed)
            return await self.cycle_items(ctx, user_area)

        if member is not None:
            user_ = member
            user_area = UserFavourites(user_id=member.id, database=self.bot.database)
            if not user_area.is_public:
                return await ctx.send("Oops! This user has their recommended firewalled (Private).")
        else:
            user_ = ctx.author
            user_area = UserFavourites(user_id=ctx.author.id, database=self.bot.database)
        if user_area.amount_of_items <= 0:
            embed = discord.Embed(color=self.bot.colour) \
                .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
            embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                f"have anything in {'your' if member is None else 'their'} favourites,\n" \
                                f" lets get filling it!"
            embed.set_thumbnail(url=random.choice(SAD_URL))
            embed.set_author(name=f"{user_.name}'s {user_area.type}", icon_url=user_.avatar_url)
            return await ctx.send(embed=embed)
        else:
            embeds = await self.generate_embeds(user=user_, area=user_area)
            if len(embeds) > 1:
                pager = Paginator(embed_list=embeds,
                                  bot=self.bot,
                                  message=ctx.message,
                                  colour=self.bot.colour)
                return self.bot.loop.create_task(pager.start())
            return await ctx.send(embed=embeds[0])

    @commands.command(
        aliases=['myr', 'recommended', 'myrecommended', 'reccomended', 'reccommended'])
    async def my_recommended(self, ctx, option=None):
        """ Get your or someone else's recommended list
            args:
                option - This can be any string but can only be valid as a bool
                         or a member to be used by the member converter but not Both.
                         In this case Member will always be picked over the cycle option.
        """

        cycle = False
        member = None

        if option is not None:
            cycle = option.lower() == "--cycle" or option.lower() == "-c"

            try:
                member = await convert_member(ctx, option)
            except commands.BadArgument:
                member = None

        if cycle:
            user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
            if user_area.amount_of_items <= 0:
                embed = discord.Embed(color=self.bot.colour) \
                    .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
                embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                    f"have anything in {'your' if member is None else 'their'} recommended,\n" \
                                    f" lets get filling it!"
                embed.set_thumbnail(url=random.choice(SAD_URL))
                embed.set_author(
                    name=f"{ctx.author.name}'s {user_area.type}",
                    icon_url=ctx.author.avatar_url
                )
                return await ctx.send(embed=embed)
            return await self.cycle_items(ctx, user_area)

        if member is not None:
            user_ = member
            user_area = UserRecommended(user_id=member.id, database=self.bot.database)
            if not user_area.is_public:
                return await ctx.send("Oops! This user has their recommended firewalled (Private).")
        else:
            user_ = ctx.author
            user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
        if user_area.amount_of_items <= 0:
            embed = discord.Embed(color=self.bot.colour) \
                .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
            embed.description = f"Oops! {'You' if member is None else 'They'} dont " \
                                f"have anything in {'your' if member is None else 'their'} recommended,\n" \
                                f" lets get filling it!"
            embed.set_thumbnail(url=random.choice(SAD_URL))
            embed.set_author(name=f"{user_.name}'s {user_area.type}", icon_url=user_.avatar_url)
            return await ctx.send(embed=embed)
        else:
            embeds = await self.generate_embeds(user=user_, area=user_area)
            if len(embeds) > 1:
                pager = Paginator(embed_list=embeds,
                                  bot=self.bot,
                                  message=ctx.message,
                                  colour=self.bot.colour)
                return self.bot.loop.create_task(pager.start())
            return await ctx.send(embed=embeds[0])


class RemoveTracked(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="removewatchlist", aliases=['rw'])
    async def remove_watchlist(self, ctx: commands.Context, index=None):
        """ Remove something from watch list """
        user_area = UserWatchlist(user_id=ctx.author.id, database=self.bot.database)
        if index is None:
            await ctx.send(
                "Oops! You haven't given me a number that matches to your list, check your list here:")
            command: commands.Command = self.bot.get_command("my_watchlist")
            return await command.invoke(ctx)
        try:
            index = int(index)
        except ValueError:
            await ctx.send(
                "Oops! You appear to have given me something that is not a number, to remove "
                "a item specify the number that is listed next to the item.\n"
                f"Example command: `{ctx.prefix}rw 1`")
            command: commands.Command = self.bot.get_command("my_watchlist")
            return await command.invoke(ctx)

        if index < 0:
            return await ctx.send(
                "<:cheeky:717784139226546297> You cant remove a negative number silly!")
        if index - 1 in range(0, user_area.amount_of_items):
            deleted = user_area.remove_content(index - 1)
            return await ctx.send(
                f"{random.choice(RANDOM_EMOJIS)} All done! Ive removed {deleted['name']}")

    @commands.command(name="removefavourite", aliases=['rf'])
    async def remove_favourites(self, ctx: commands.Context, index=None):
        """ Remove something from favourites list """
        user_area = UserFavourites(user_id=ctx.author.id, database=self.bot.database)
        if index is None:
            await ctx.send(
                "Oops! You haven't given me a number that matches to your list, check your list here:")
            command: commands.Command = self.bot.get_command("my_favourites")
            return await command.invoke(ctx)

        try:
            index = int(index)
        except ValueError:
            await ctx.send(
                "Oops! You appear to have given me something that is not a number, to remove "
                "a item specify the number that is listed next to the item.\n"
                f"Example command: `{ctx.prefix}rf 1`")
            command: commands.Command = self.bot.get_command("my_favourites")
            return await command.invoke(ctx)

        if index < 0:
            return await ctx.send(
                "<:cheeky:717784139226546297> You cant remove a negative number silly!")
        if index - 1 in range(0, user_area.amount_of_items):
            deleted = user_area.remove_content(index - 1)
            return await ctx.send(
                f"{random.choice(RANDOM_EMOJIS)} All done! Ive removed {deleted['name']}")

    @commands.command(name="removerecommended",
                      aliases=['rr', 'removereccommended', 'removereccomended'])
    async def remove_recommended(self, ctx, index=None):
        """ Remove something from recommended list """

        user_area = UserRecommended(user_id=ctx.author.id, database=self.bot.database)
        if index is None:
            await ctx.send(
                "Oops! You haven't given me a number that matches to your list, check your list here:")
            command: commands.Command = self.bot.get_command("my_recommended")
            return await command.invoke(ctx)

        try:
            index = int(index)
        except ValueError:
            await ctx.send(
                "Oops! You appear to have given me something that is not a number, to remove "
                "a item specify the number that is listed next to the item.\n"
                f"Example command: `{ctx.prefix}rr 1`")
            command: commands.Command = self.bot.get_command("my_recommended")
            return await command.invoke(ctx)

        if index < 0:
            return await ctx.send(
                "<:cheeky:717784139226546297> You cant remove a negative number silly!")
        if index - 1 in range(0, user_area.amount_of_items):
            deleted = user_area.remove_content(index - 1)
            return await ctx.send(
                f"{random.choice(RANDOM_EMOJIS)} All done! Ive removed {deleted['name']}")


def setup(bot):
    bot.add_cog(AddingAnime(bot))
    bot.add_cog(UserSettings(bot))
    bot.add_cog(ViewTracked(bot))
    bot.add_cog(RemoveTracked(bot))
