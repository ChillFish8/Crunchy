import re
import discord
import asyncio
import json
from discord.ext import commands

from database.database import UserFavourites, UserRecommended, UserWatchlist

with open("command_settings.json", "r") as file:
    COMMAND_SETTINGS = json.load(file)

FALSE_PREMIUM_MAX_IN_STORE = COMMAND_SETTINGS.get("nopremium_max_per_storage")
TRUE_PREMIUM_MAX_IN_STORE = COMMAND_SETTINGS.get("premium_max_per_storage")
PREMIUM_URL = COMMAND_SETTINGS.get("premium_url")


async def add_watchlist(ctx, bot, name, url):
    user_tracker: UserWatchlist = UserWatchlist(user_id=ctx.author.id, database=bot.database)
    if (user_tracker.amount_of_items >= FALSE_PREMIUM_MAX_IN_STORE) and (ctx.has_voted == 0):
        return {'content': "<:HimeMad:676087826827444227> Oh no! "
                           "You dont have enough space in your watchlist "
                           "to add this, get more storage by voting here "
                           "https://top.gg/bot/656598065532239892/vote"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[0]) and (ctx.has_voted == 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh no! "
                           f"You seem to have maxed out your watchlist, you can get more by"
                           f" buying premium here to help support my development: {PREMIUM_URL}"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[1]) and (ctx.has_voted > 1):
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
    if (user_tracker.amount_of_items >= FALSE_PREMIUM_MAX_IN_STORE) and (ctx.has_voted == 0):
        return {'content': "<:HimeMad:676087826827444227> Oh no! "
                           "You dont have enough space in your favourites "
                           "to add this, get more storage by voting here "
                           "https://top.gg/bot/656598065532239892/vote"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[0]) and (ctx.has_voted == 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh no! "
                           f"You seem to have maxed out your favourites, you can get more by"
                           f" buying premium here to help support my development: {PREMIUM_URL}"
                }
    elif (user_tracker.amount_of_items >= TRUE_PREMIUM_MAX_IN_STORE[1]) and (ctx.has_voted > 1):
        return {'content': f"<:HimeMad:676087826827444227> Oh wow! "
                           f"You've managed to add over {TRUE_PREMIUM_MAX_IN_STORE[1]} things to your favourites area! "
                           f"However, you'll need to either delete some to add more or contact my developer"
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
            return (str(r.emoji) in BASE_EMOJIS) and (u.id == ctx.author.id) and (r.message.id == message.id)

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.delete()
            return await ctx.send(content="The selection period has expired.")

        results = await self.options[BASE_EMOJIS.index(str(reaction.emoji))](ctx, self.bot, name, url)
        if not isinstance(results, tuple):
            if not results:
                await message.delete()
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to your list!")
            else:
                await message.delete()
                return await ctx.send(**results)
        else:
            if not results[0] or not results[1]:
                await message.delete()
                return await ctx.send(
                    "<:HimeSad:676087829557936149> Oh no! Something went wrong adding that to your list!")
            else:
                for res in results:
                    if not res['content'].startswith("<:HimeHappy:677852789074034691>"):
                        return await ctx.send(**res)
                else:
                    await message.delete()
                    return await ctx.send(f"<:HimeHappy:677852789074034691> Success!"
                                          f""" I've added "{name}" to both your watchlist and favourites!""")

    @commands.command(aliases=['recc'])
    async def recommend(self, ctx, user: discord.Member = None, *, argument: str = None):
        """ Add Anime to to someone's recommended list """
        if user is None:
            return await ctx.send(f"<:HimeMad:676087826827444227> Oops! "
                                  f"You didnt mention the person you wanted to recommend an Anime to.")

        user_area = UserRecommended(user_id=user.id, database=self.bot.database)
        if not user_area.is_public:
            return await ctx.send(f"<:HimeMad:676087826827444227> Oops! "
                                  f"The user you mentioned has their recommended list set to private.")

        if argument is None:
            return await ctx.send(f"<:HimeMad:676087826827444227> Oh no! "
                                  f"You didnt give me anything to add to {user.display_name}'s recommended list."
                                  f" Do `{ctx.prefix}help recommended` for more info.")

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

        try:
            user_area.add_content({'name': name, 'url': url})
            return await ctx.send(f"<:HimeHappy:677852789074034691> Success!"
                                  f""" I've added "{name}" to {user.name}'s recommended list.""")
        except Exception as e:
            return await ctx.send(f"Oh no! A error jumped out and scared me: {e}")


def setup(bot):
    bot.add_cog(AddingAnime(bot))
