import discord
import asyncio

from discord.ext import commands

from realms.user_characters import UserCharacters
from realms.character import Character
from realms.datastores.database import MongoDatabase
from realms.static import Database


class Party:
    def __init__(self, bot, ctx: commands.Context, user_area: UserCharacters, **options):
        self.bot = bot
        self.ctx = ctx
        self.user_area = user_area
        self._characters = list(map(lambda c: Character().from_dict(c), user_area.characters))

        amount, rem = divmod(len(self._characters), 10)
        if rem:
            amount += 1
        self._total_pages = amount - 1
        self._selected_party = {
            0: {},
            1: {},
            2: {},
            3: {},
        }
        self._users = []

        self._active_message = None
        self._pointer = 0
        self._page_no = 0

        self.select_emoji = {
            '⬆️': self.up,
            '⬇️': self.down,
            '<:True:688518995997098063>': self.select,
            '<:False:688518995997098058>': self.un_select,
            '◀️': self.page_left,
            '▶️': self.page_right,
            '⚔️': self.confirm,
        }

    def format_characters(self, chars: list, target_pos: int = 0):
        texts = []
        current = "```prolog\n"
        for i, character in enumerate(chars):
            if i == target_pos:
                current += f">>> [{i + (10 * self._page_no) + 1}] {character.name.title()}\n"
            else:
                current += f"[{i + (10 * self._page_no) + 1}] {character.name.lower()}\n"
            if ((i + 1) % 5) == 0:
                current += "```"
                texts.append(current)
                current = "```prolog\n"

        current += "```"
        texts.append(current)
        return texts

    def generate_embed(self):
        embed = discord.Embed(color=self.bot.colour)
        embed.set_author(name=f"{self.ctx.author.name}'s Party", icon_url=self.ctx.author.avatar_url)
        chars = self._characters[self._page_no * 10: self._page_no * 10 + 10]
        if self._pointer >= len(chars):
            self._pointer = (len(chars) - 1)
        sections = self.format_characters(chars, target_pos=self._pointer)

        # Character Lists
        embed.add_field(name="Characters | 1", value=sections[0])
        embed.add_field(name="Characters | 2", value=sections[1])

        embed.add_field(
            name="Selected Character Stats:",
            value=f"```prolog\n"
                  f'Name: "{chars[self._pointer].name.title()}"   '
                  f"Level: {chars[self._pointer].level}   "
                  f"HitPoints: {123}\n```",
            inline=False
        )

        selected_str = ""
        for key, selected in self._selected_party.items():
            selected_str += f"`{key + 1}. {selected.get('name', 'None Selected')}`\n"
        embed.add_field(name="Selected Characters", value=selected_str)

        embed.add_field(name="Team Members", value="\u200b" + "\n".join(self._users))
        return embed

    def check(self, r: discord.Reaction, u: discord.User):
        return (r.message.id == self._active_message.id) and \
               (str(r.emoji) in self.select_emoji) and \
               (u.id == self.ctx.author.id)

    def up(self):
        if self._pointer != 0:
            self._pointer -= 1

    def down(self):
        if self._pointer + 1 < len(self._characters):
            self._pointer += 1

    def page_left(self):
        if self._page_no != 0:
            self._page_no -= 1

    def page_right(self):
        if self._page_no < self._total_pages:
            self._page_no += 1

    def select(self):
        pass

    def un_select(self):
        pass

    def confirm(self):
        pass

    async def start(self):
        self._active_message = await self.ctx.send(embed=self.generate_embed())
        for emoji in self.select_emoji:
            await self._active_message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=self.check)
                self.select_emoji[str(reaction.emoji)]()
            except asyncio.TimeoutError:
                return await self._active_message.edit(
                    embed=None, content="The Embed has ended after being left inactive.")

            await self._active_message.edit(embed=self.generate_embed())


class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="selectparty", aliases=['setparty'])
    async def select_party(self, ctx: commands.Context):
        user_area = UserCharacters(ctx.author.id, Database.db)
        user_party = Party(self.bot, ctx, user_area)
        await user_party.start()

    @commands.command(name="party")
    async def party(self, ctx: commands.Context):
        pass

    @commands.command(name="invitetoparty", aliases=['itp', 'partyinvite', 'partyinv'])
    async def invite_user_to_party(self, ctx: commands.Context, member: discord.User):
        pass

    @commands.command(name="removefromparty", aliases=['rfp', 'remparty', 'partyremove'])
    async def remove_from_party(self, ctx: commands.Context, member: discord.User):
        pass


def setup(bot):
    bot.add_cog(MarketCog(bot))
