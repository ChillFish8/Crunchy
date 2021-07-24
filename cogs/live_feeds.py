import os
from typing import Union, Any, Optional

import aiohttp
import discord
import asyncio
import random

from discord.ext import commands
from data.guild_config import GuildWebhooks

# Urls
RELEASE_RSS = "http://feeds.feedburner.com/crunchyroll/rss/anime"
NEWS_RSS = "http://feeds.feedburner.com/crunchyroll/animenews"
API_BASE = "https://crunchy-bot.live/api/anime"
NEW_API = "https://api.crunchy.gg/v0/events"

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


async def make_webhook(
        author: discord.Member,
        channel: discord.TextChannel,
        feed_type,
):
    with open(PFP_PATH, 'rb') as file:
        new_webhook = await channel.create_webhook(
            name=f'Crunchyroll {feed_type.capitalize()}',
            avatar=file.read(),
            reason=f"Crunchy will use this webhook to send like updates, authorized by: {author}"
        )
        return new_webhook


def check_exists(name, hooks) -> Optional[discord.Webhook]:
    """ Getting current web hooks """
    for hook in hooks:
        if name.lower().replace(" ", "") in hook.name.lower().replace(" ", ""):
            return hook
    return


class LiveFeedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None

    async def ensure_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def set_webhook(self, target: str, guild_id: int, webhook_url: str) -> int:
        payload = {
            "guild_id": str(guild_id),
            "webhook_url": webhook_url,
        }

        headers = {
            "Authorization": os.getenv("NEW_API_KEY")
        }

        session = await self.ensure_session()
        async with session.post(
                f"{NEW_API}/{target}/update",
                json=payload,
                headers=headers,
        ) as resp:
            return resp.status

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addreleasechannel", aliases=['arc', 'addrelease'])
    async def add_release_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Let just make sure they cant have multiple hooks at once
        hook = check_exists(name="Crunchyroll Releases", hooks=existing_hooks)
        if hook is not None:
            message = await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a release webhook (`{hook.name}`) active.\n"
                f"Would you like me to reload this webhook?.")
            await message.add_reaction("<:ok:717784139943641088>")

            def check(r, u):
                return str(r.emoji) == "<:ok:717784139943641088>" \
                       and u.id == ctx.author.id \
                       and r.message.id == message.id

            try:
                await self.bot.wait_for("reaction_add", timeout=30, check=check)
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"<:HimeSad:676087829557936149> The selection period has timed out, "
                    f"Please delete the webhook manually if you haven't already.")
            else:
                await message.delete()
                to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
                status = await self.set_webhook("releases", ctx.guild.id, hook.url)
                if status != 200:
                    return await to_edit.edit(
                        content="<:HimeSad:676087829557936149> Sorry, something went wrong on our end >-<."
                                " Please try again later."
                    )

                await hook.send(
                    random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
                return await to_edit.edit(
                    f'All set! I will now send releases to <#{hook.channel_id}>')

        to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
        try:
            webhook = await make_webhook(ctx.author, channel, feed_type="releases")
        except discord.Forbidden:
            return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                              "I need the permission `MANAGE_WEBHOOKS`.")
        except AttributeError:
            return await to_edit.edit(
                content="Sorry but something went wrong when trying to make this webhook."
                        " Please try a different channel."
            )

        status = await self.set_webhook("releases", ctx.guild.id, webhook.url)
        if status != 200:
            return await to_edit.edit(
                content="<:HimeSad:676087829557936149> Sorry, something went wrong on our end >-<."
                        " Please try again later."
            )

        await webhook.send(
            random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
        return await to_edit.edit(
            content=f'All set! I will now send releases to <#{webhook.channel_id}>')

    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="addnewschannel", aliases=['acc', 'addnews'])
    async def add_news_channel(self, ctx, channel: discord.TextChannel):
        existing_hooks = await ctx.guild.webhooks()  # Let just make sure they cant have multiple hooks at once
        hook = check_exists(name="Crunchyroll News", hooks=existing_hooks)
        if hook is not None:
            message = await ctx.send(
                f"<:HimeSad:676087829557936149> Oops! Already have a news webhook (`{hook.name}`) active.\n"
                f"Would you like me to reload this webhook?.")
            await message.add_reaction("<:ok:717784139943641088>")

            def check(r, u):
                return str(r.emoji) == "<:ok:717784139943641088>" \
                       and u.id == ctx.author.id \
                       and r.message.id == message.id

            try:
                await self.bot.wait_for("reaction_add", timeout=30, check=check)
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"<:HimeSad:676087829557936149> The selection period has timed out, "
                    f"Please delete the webhook manually if you haven't already.")
            else:
                await message.delete()
                to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
                status = await self.set_webhook("news", ctx.guild.id, hook.url)
                if status != 200:
                    return await to_edit.edit(
                        content="<:HimeSad:676087829557936149> Sorry, something went wrong on our end >-<."
                                " Please try again later."
                    )

                await hook.send(
                    random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
                return await to_edit.edit(
                    content=f'All set! I will now send news to <#{hook.channel_id}>')

        to_edit = await ctx.send("<:cheeky:717784139226546297> One moment...")
        try:
            webhook = await make_webhook(ctx.author, channel, feed_type="news")
        except discord.Forbidden:
            return await to_edit.edit(content="I am missing permissions to create a webhook. "
                                              "I need the permission `MANAGE_WEBHOOKS`.")
        except AttributeError:
            return await to_edit.edit(
                content="Sorry but something went wrong when trying to make this webhook."
                        " Please try a different channel."
            )

        status = await self.set_webhook("news", ctx.guild.id, webhook.url)
        if status != 200:
            return await to_edit.edit(
                content="<:HimeSad:676087829557936149> Sorry, something went wrong on our end >-<."
                        " Please try again later."
            )

        await webhook.send(
            random.choice(RANDOM_EMOJIS) + "Hello world! *phew* i got through!")
        return await to_edit.edit(
            content=f'All set! I will now send news to <#{webhook.channel_id}>')

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

