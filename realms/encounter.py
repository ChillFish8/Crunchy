import discord
import asyncio

from random import randint
from discord.ext import commands

from realms.parties import Party
from realms.generation.monsters import MonsterManual, Monster

HIME_CHEEK = "https://cdn.discordapp.com/emojis/717784139226546297.png?v=1"
EMOJI = [

]


class Encounter:
    def __init__(self, bot, ctx, party: Party, submit):
        self.bot = bot
        self.ctx: commands.Context = ctx
        self.party = party
        self.monster_manual = MonsterManual()
        self.monster = None
        self.submit_callback = submit

    def get_rand_monster(self) -> Monster:
        cr = randint(self.party.challenge_rating, self.party.challenge_rating + 5)
        monster = self.monster_manual.get_random_monster(cr)
        return monster

    async def menu(self):
        random_monsters = []
        block = f"Which quest do you choose? Do `{self.ctx.prefix}accept <quest number>`\n\n"
        for i in range(4):
            monster = self.get_rand_monster()
            block += f"**{i + 1}) - {monster.format_name}**\n"
            random_monsters.append(monster)
        embed = discord.Embed(title="Monster Quests!", color=self.bot.colour)
        embed.description = block
        embed.set_footer(text="Limited to 4 encounters per 12 hours without voting.")
        msg = await self.ctx.send(embed=embed)
        self.submit_callback(self.ctx)
        try:
            quest_no, _ = await self.bot.wait_for(
                'quest_accept',
                timeout=120,
                check=lambda no, user: user.id == self.ctx.author.id
            )
            self.monster = random_monsters[quest_no - 1]
            return await self.battle()
        except asyncio.TimeoutError:
            await msg.delete()

    async def battle(self):
        def check(msg: discord.Message):
            return (msg.author.id == self.ctx.author.id) and\
                   (msg.channel.id == self.ctx.channel.id) and msg.content.startswith(self.ctx.prefix)

        content = self.get_content(start=True)
        await self.ctx.send(content)
        valid = False
        while not valid:
            try:
                message = await self.bot.wait_for('message', timeout=120, check=check)
                command, *args = message.content.split(" ")
                await self.process_commands_internally(command, args)

            except asyncio.TimeoutError:
                return await self.ctx.send("📛 This battle has expired! This is counted as failing to complete the quest.")

        battling = True
        while battling:
            content = self.get_content()
            await self.ctx.send(content)
            try:
                message = await self.bot.wait_for('message', timeout=30, check=check)
                print(message.content)
            except asyncio.TimeoutError:
                battling = False
                await self.ctx.send("📛 This battle has expired! This is counted as failing to complete the quest.")

    def get_content(self, start=False) -> str:
        if start:
            return f"**Roll initiative! Do:** `{self.ctx.prefix}roll 1d20`"
        else:
            return "nom"

    async def process_commands_internally(self, command: str, args: list):
        p
