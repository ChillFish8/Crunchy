from typing import Union, Any

import discord
import asyncio
import random

from discord.ext import commands
from data.guild_config import GuildWebhooks

# Urls
RELEASE_RSS = "http://feeds.feedburner.com/crunchyroll/rss/anime"
NEWS_RSS = "http://feeds.feedburner.com/crunchyroll/animenews"
API_BASE = "https://crunchy-bot.live/api/anime"

# Black list
EXCLUDE_IN_TITLE = [
    'dub)',
    '(russian',
    '(spanish',
]

# Embed Option
COLOUR = 0xe87e15
CR_LOGO = "https://cdn.discordapp.com/emojis/676087821596885013.png?v=1"
RANDOM_THUMBS = [
    'https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784215986634953/cheeky.png',
    'https://cdn.discordapp.com/attachments/680350705038393344/717784211771097179/thank_you.png'
]
RANDOM_EMOJIS = [
    '<:thank_you:717784142053507082>',
    '<:cheeky:717784139226546297>',
    '<:exitment:717784139641651211>',
]

PFP_PATH = r'resources/photos/crunchy_image.png'


class LiveFeedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def check_exists(cls, name, hooks) -> Union[bool, discord.Webhook]:
        """ Getting current web hooks """
        for hook in hooks:
            if name.lower().replace(" ", "") in hook.name.lower().replace(" ", ""):
                return hook
        else:
            return False

    @classmethod
    async def make_webhook(cls, channel, feed_type):
        with open(PFP_PATH, 'rb') as file:
            new_webhook = await channel.create_webhook(
                name=f'Crunchyroll {feed_type.capitalize()}', avatar=file.read())
            return new_webhook

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addreleasechannel", aliases=['arc', 'addrelease'])
    async def add_release_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Lest just make sure they cant have multiple hooks at once
        hook = self.check_exists(name="Crunchyroll Releases", hooks=existing_hooks)
        if hook:
            message = await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a release webhook (`{hook.name}`) active.\n"
                f"Would you like me to reload this webhook?.")
            await message.add_reaction("<:ok:717784139943641088>")
            try:
                def check(r, u):
                    return str(r.emoji) == "<:ok:717784139943641088>" \
                           and u.id == ctx.author.id \
                           and r.message.id == message.id

                choice = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                if choice:
                    await message.delete()
                    to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
                    guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
                    webhook = hook
                else:
                    return
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"<:HimeSad:676087829557936149> The selection period has timed out, "
                    f"Please delete the webhook manually if you haven't already.")
        else:
            to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
            guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
            try:
                webhook = await self.make_webhook(channel=channel, feed_type="releases")
            except discord.Forbidden:
                return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                                  "I need the permission `MANAGE_WEBHOOKS`.")
            except AttributeError:
                return await to_edit.edit(
                    content="Sorry but something went wrong when trying to make this webhook."
                            " Please try a different channel.")

        guild_data.add_webhook(webhook=webhook, feed_type="releases")
        await webhook.send(content=random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
        return await to_edit.edit(content=f'All set! I will now send releases to <#{webhook.channel_id}>')

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addnewschannel", aliases=['acc', 'addnews'])
    async def add_news_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Lest just make sure they cant have multiple hooks at once
        hook = self.check_exists(name="Crunchyroll News", hooks=existing_hooks)
        if hook:
            message = await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a news webhook (`{hook.name}`) active.\n"
                f"Would you like me to reload this webhook?.")
            await message.add_reaction("<:ok:717784139943641088>")
            try:
                def check(r, u):
                    return str(r.emoji) == "<:ok:717784139943641088>" \
                           and u.id == ctx.author.id \
                           and r.message.id == message.id

                choice = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                if choice:
                    await message.delete()
                    to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
                    guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
                    webhook = hook
                else:
                    return
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"<:HimeSad:676087829557936149> The selection period has timed out, "
                    f"Please delete the webhook manually if you haven't already.")
        else:
            to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
            guild_data: GuildWebhooks = GuildWebhooks(guild_id=ctx.guild.id, database=self.bot.database)
            try:
                webhook = await self.make_webhook(channel=channel, feed_type="news")
            except discord.Forbidden:
                return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                                  "I need the permission `MANAGE_WEBHOOKS`.")
            except AttributeError:
                return await to_edit.edit(
                    content="Sorry but something went wrong when trying to make this webhook."
                            " Please try a different channel.")

        guild_data.add_webhook(webhook=webhook, feed_type="news")
        await webhook.send(content=random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
        return await to_edit.edit(content=f'All set! I will now send news to <#{webhook.channel_id}>')

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Sorry! You're missing the require permission `ADMINISTRATOR`"
                f"to use this command (`{ctx.command}`)")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> You need to mention a channel"
                " or give me a channel Id for this command.")

        elif isinstance(error, discord.Forbidden):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Oops! Looks like i dont have permission to do this command.")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(
                "<:HimeSad:676087829557936149> Oops! I cant see that channel or "
                "it is invalid, please try a different one.")
        else:
            raise error

def setup(bot):
    bot.add_cog(LiveFeedCommands(bot))

