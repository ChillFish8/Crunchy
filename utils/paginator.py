import discord
import asyncio


class Paginator:
    FIRST_EMOJI = "\u23EE"  # [:track_previous:]
    LEFT_EMOJI = "\u2B05"  # [:arrow_left:]
    RIGHT_EMOJI = "\u27A1"  # [:arrow_right:]
    LAST_EMOJI = "\u23ED"  # [:track_next:]
    DELETE_EMOJI = "\u274c"  # [:x:]

    PAGINATION_EMOJI = [FIRST_EMOJI, LEFT_EMOJI, DELETE_EMOJI, RIGHT_EMOJI, LAST_EMOJI]

    def __init__(self, embed_list, message: discord.Message, bot, colour):
        self.embed_list = embed_list
        self.channel = message.channel
        self.message = message
        self.counter = 0
        self.old_message = None
        self.bot = bot
        self.colour = colour

    async def start(self):
        self.old_message = await self.channel.send(embed=self.embed_list[self.counter])
        for emoji in self.PAGINATION_EMOJI:
            await self.old_message.add_reaction(emoji)
        await self.pager()

    async def pager(self):
        def check(r, u):
            return (u.id == self.message.author.id) and \
                   (str(r.emoji) in self.PAGINATION_EMOJI) and\
                   (r.message.id == self.old_message.id)

        running = True
        while running:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == self.PAGINATION_EMOJI[0]:
                    running = await self.first()
                elif str(reaction.emoji) == self.PAGINATION_EMOJI[1]:
                    running = await self.previous()
                elif str(reaction.emoji) == self.PAGINATION_EMOJI[2]:
                    running = await self.stop_pagination()
                elif str(reaction.emoji) == self.PAGINATION_EMOJI[3]:
                    running = await self.next()
                elif str(reaction.emoji) == self.PAGINATION_EMOJI[4]:
                    running = await self.end()

            except asyncio.TimeoutError:
                try:
                    embed = discord.Embed(title="Pagination Ended",
                                          color=self.colour)
                    await self.old_message.edit(embed=embed)
                except discord.NotFound:
                    pass
                running = False

    async def first(self):
        self.counter = 0
        await self.old_message.edit(embed=self.embed_list[self.counter])
        return True

    async def previous(self):
        if self.counter != 0:
            self.counter -= 1
            await self.old_message.edit(embed=self.embed_list[self.counter])
        return True

    async def stop_pagination(self):
        embed = discord.Embed(title="Pagination Ended",
                              color=self.colour)
        await self.old_message.edit(embed=embed)
        return False

    async def next(self):
        if self.counter < len(self.embed_list) - 1:
            self.counter += 1
            await self.old_message.edit(embed=self.embed_list[self.counter])
        return True

    async def end(self):
        self.counter = len(self.embed_list) - 1
        await self.old_message.edit(embed=self.embed_list[self.counter])
        return True
