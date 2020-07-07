import discord
import asyncio

from discord.ext import commands

from realms.user_characters import UserCharacters
from realms.character import Character
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

        self._db = Database.db

        data = self._db.get_party(ctx.author.id)
        if data is not None:
            self._selected_party = data.get('party_choice')
        else:
            self._selected_party = {
                '0': {},
                '1': {},
                '2': {},
                '3': {},
            }
        self._users = []

        self._active_message = None
        self._pointer = 0
        self._page_no = 0
        self._temp_characters = []

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
        self._temp_characters = self._characters[self._page_no * 10: self._page_no * 10 + 10]
        if self._pointer >= len(self._temp_characters):
            self._pointer = (len(self._temp_characters) - 1)
        sections = self.format_characters(self._temp_characters, target_pos=self._pointer)

        # Character Lists
        embed.add_field(name="Characters | 1", value=sections[0])
        embed.add_field(name="Characters | 2", value=sections[1])

        embed.add_field(
            name="Selected Character Stats:",
            value=f"```prolog\n"
                  f'Name: "{self._temp_characters[self._pointer].name.title()}"   '
                  f"Level: {self._temp_characters[self._pointer].level}   "
                  f"HitPoints: {123}\n```",
            inline=False
        )

        selected_str = ""
        for key, selected in self._selected_party.items():
            selected_str += f"`{int(key) + 1}. {selected.get('name', 'None Selected')}`\n"
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
        target = self._temp_characters[self._pointer]
        for char in self._selected_party:
            if self._selected_party[char].get('name') == target.name:
                return
            elif not self._selected_party[char]:
                self._selected_party[char] = {'name': target.name, 'id': target.id}
                return

    def un_select(self):
        target = self._temp_characters[self._pointer]
        for char in self._selected_party:
            if self._selected_party[char].get('name') == target.name:
                self._selected_party[char] = {}
                return

    def confirm(self):
        self._db.update_any_party(self.ctx.author.id, party_choice=self._selected_party)
        return True

    async def start(self):
        self._active_message = await self.ctx.send(embed=self.generate_embed())
        for emoji in self.select_emoji:
            await self._active_message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=self.check)
                if self.select_emoji[str(reaction.emoji)]():
                    await self._active_message.delete()
                    return await self.ctx.send("Your party choice has been saved!")
            except asyncio.TimeoutError:
                await self._active_message.clear_reactions()
                return await self._active_message.edit(
                    embed=None, content="The Embed has ended after being left inactive.")

            await self._active_message.edit(embed=self.generate_embed())

    @property
    def party(self):
        return list(map(lambda c: f"**• {c.get('name')}**", self._selected_party.values()))
    
    @property
    def challenge_rating(self):
        total_level = 0
        for char in self._selected_party.values():
            if char.get('id'):
                char = self.user_area.get_character(id_=char.get('id'))
            else:
                char = self.user_area.get_character(search=char.get('name'))
            char = Character().from_dict(char)
            total_level += char.level
        return (total_level // 5) + 1
