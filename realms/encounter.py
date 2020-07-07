import discord
import asyncio
import re
import itertools

from random import randint, choice
from discord.ext import commands

from realms.parties import Party
from realms.generation.monsters import MonsterManual, Monster

HIME_CHEEK = "https://cdn.discordapp.com/emojis/717784139226546297.png?v=1"
dice_regex = re.compile("^([1-9]*)[dD]([1-9][0-9]*)")


class PartialCommand:
    def __init__(self, command: str, *args, **kwargs):
        self.command = command.lower()
        self.args = args
        self.kwargs = kwargs

    @property
    def args_to_str(self):
        return "" + " ".join(self.args)


class Encounter:
    def __init__(self, bot, ctx, party: Party, submit):
        self.bot = bot
        self.ctx: commands.Context = ctx
        self.party = party
        self.monster_manual = MonsterManual()
        self.monster = None
        self.submit_callback = submit
        self.turn = None

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
            return (msg.author.id == self.ctx.author.id) and \
                   (msg.channel.id == self.ctx.channel.id) and \
                    msg.content.startswith(self.ctx.prefix)

        content = await self.get_content(start=True)
        await self.ctx.send(content)
        valid = False
        while not valid:
            try:
                message = await self.bot.wait_for('message', timeout=120, check=check)
                command, *args = message.content.split(" ")
                result = await self.process_commands_internally(command, args)
                if result.command == "roll":
                    user_initiative = self.process_roll(result.args_to_str)
                    if user_initiative in range(1, 21):
                        valid = True
                        content = await self.get_content(stage=0, user_initiative=user_initiative)
                        await self.ctx.send(content)
            except asyncio.TimeoutError:
                return await self.ctx.send("📛 This battle has expired! This is counted as failing to complete the quest.")

        stage = 1
        battling = True
        while battling:
            content = await self.get_content(stage=stage)
            if content is None:
                pass
            elif content == -1:
                return await self.ctx.send(
                    "📛 This battle has expired! This is counted as failing to complete the quest.")
            else:
                await self.ctx.send(content)
            battling = False

    async def get_content(self, start=False, stage=0, **kwargs):
        if start:
            return f"**You accepted the challenge against `{self.monster.name}`.\n Roll initiative! Do:** `{self.ctx.prefix}roll 1d20`"
        elif stage == 0:
            if self.monster.initiative > kwargs.get('user_initiative'):
                self.turn = itertools.cycle([self.monster_turn, self.human_turn])
                return f"**The monster rolled a {self.monster.initiative}, you rolled a {kwargs.get('user_initiative')}.**" \
                       f" <:HimeSad:676087829557936149> **it goes first!**"
            else:
                self.turn = itertools.cycle([self.human_turn, self.monster_turn])
                return f"**The monster rolled a {self.monster.initiative}, you rolled a {kwargs.get('user_initiative')}.**" \
                       f" <:cheeky:717784139226546297> **you go first!**"
        else:
            return await self.human_turn()
            # return await next(self.turn)()

    async def human_turn(self):
        mana = 6
        cards = {
            0: choice(self.party.selected_characters),
            1: choice(self.party.selected_characters),
            2: choice(self.party.selected_characters),
            3: choice(self.party.selected_characters),
            4: choice(self.party.selected_characters),
        }

        card_block = ""
        for i, card in enumerate(cards.values()):
            card_block += f"**`{i + 1}) - {card.name} - [ Level: {card.level}, HP: {card.hp} ]`**\n"

        text = f"__**This round's deck**__\n" \
               f"Pick any amount of cards upto 5.\n" \
               f" you can stack cards to increase damage but beware of the cost.\n\n" \
               f"💎 **Mana Cost:**\n" \
               f"• 1 stack ( 1x damage ) - Costs 1 Mana\n" \
               f"• 2 stack ( 2x damage ) - Costs 3 Mana\n" \
               f"• 3 stack ( 3x damage ) - Costs 6 Mana\n\n" \
               f"<:mana_bottle:730069998240006174> **Mana:** `{mana}`\n" \
               f"\n" \
               f"⚔️ **Cards:**\n" \
               f"{card_block}"

        await self.ctx.send(text)

    async def monster_turn(self):
        return "oh no!"

    @staticmethod
    def process_roll(dice: str, expected=(1, 20)) -> int:
        if dice == "":
            return 0
        if dice[0].isalpha():
            dice = "1" + dice

        amount, dice_sides, *_ = dice_regex.findall(dice)[0]
        if {int(amount), int(dice_sides)} & set(expected):
            total = 0
            for _ in range(int(amount)):
                total += randint(1, int(dice_sides))
            return total
        else:
            return 0

    @classmethod
    async def process_commands_internally(cls, command: str, args: list):
        return PartialCommand(command, *args)
