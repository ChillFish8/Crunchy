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


class Deck:
    def __init__(self, characters: list):
        self._selected = [choice(characters) for _ in range(5)]
        self._stacked = {}
        self._attacks = []
        self._previous_stack_indexes = []
        self.character_xp_area = {}

    def stack(self, index, amount) -> (int, None):
        if len(self._stacked) >= 3:
            return -1, None

        stack = []
        char = self._selected[index]

        for i, char_ in enumerate(self._selected):
            if char_.id == char.id:
                if not self.character_xp_area.get(char.id):
                    self.character_xp_area[char.id] = 0
                self.character_xp_area[char.id] += 1
                stack.append(self._selected[i])
            if len(stack) == amount:
                self._stacked[char.id] = stack
                self._attacks.append(char_.id)
                self._previous_stack_indexes.append(index)
                return 1, stack
        return 0, None

    @property
    def show_cards(self):
        card_block = ""
        previous = []
        for i, card in enumerate(self._selected):
            if card.id in self._stacked:
                if card.id not in previous:
                    previous.append(card.id)
                    card_block += f"**`{i + 1}) - {card.name} - [ Level: {card.level}, HP: {card.hp} ] " \
                                  f"x {len(self._stacked[card.id])}`**\n"
            else:
                card_block += f"**`{i + 1}) - {card.name} - [ Level: {card.level}, HP: {card.hp} ]`**\n"
        return card_block

    @property
    def attacks(self):
        attacks = []
        for atk in self._attacks:
            attacks.append(self._stacked[atk])
        return attacks

class Encounter:
    def __init__(self, bot, ctx, party: Party, submit, user_area):
        self.bot = bot
        self.ctx: commands.Context = ctx
        self.party = party
        self.monster_manual = MonsterManual()
        self.monster = None
        self.submit_callback = submit
        self.turn = None
        self._deck = None
        self._user_area = user_area

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
            if self.monster.hp <= 0:
                await self.show_end_screen()
                battling = False
            if content is None:
                continue
            elif content == -1:
                return await self.ctx.send(
                    "📛 This battle has expired! This is counted as failing to complete the quest.")
            else:
                await self.ctx.send(content)
            await asyncio.sleep(0.5)

    async def show_end_screen(self):
        await self.ctx.send("*The monster stumbles back and finally collapses. Dead.*")
        await asyncio.sleep(2)
        text = "🎉 **Quest Complete!** 🎉\n" \
               "\n" \
               "You successfully defeated {monster}!\n" \
               "*You search through the remains of the monster to find loot*\n" \
               "\n" \
               "***You gain the following rewards:***\n" \
               "> 💠 `{plat}` **Platinum Pieces**\n" \
               "> 🔹 `{gold}` **Gold Pieces**\n" \
               "> 🔸 `{cop}` **Copper Pieces**\n"

        await self.ctx.send(
            text.format(
                monster=self.monster.name,
                plat=self.monster.loot['platinum'],
                gold=self.monster.loot['gold'],
                cop=self.monster.loot['copper']
            )
        )

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
            return await next(self.turn)()

    async def human_turn(self):
        msg = await self.ctx.send(
            f"⚔️{self.ctx.author.mention}️ **It's your turn, get ready to stack and attack!**")
        deck = Deck(self.party.selected_characters)
        self._deck = deck
        card_block = deck.show_cards

        text = f"**Monster HP:** {self.monster.hp}\n" \
               f"\n" \
               f"Pick any amount of cards to upto 3 attacks.\n" \
               f" you can stack cards to increase damage but beware of the cost.\n" \
               f"You can use `{self.ctx.prefix}stack <card number> <amount>` to stack cards and then " \
               f"`{self.ctx.prefix}attack` to launch your attack!\n\n" \
               f"💎 **Card Stacking:**\n" \
               f"• 1 stack ( 1x damage )\n" \
               f"• 2 stack ( 2x damage )\n" \
               f"• 3 stack ( 3x damage )\n" \
               f"\n" \
               f"⚔️ **Cards:**\n" \
               f"{card_block}"

        embed = discord.Embed(color=self.bot.colour)
        embed.set_author(name="This round's deck", icon_url=self.ctx.author.avatar_url)
        embed.description = text
        embed.set_footer(text=f"Use {self.ctx.prefix}stack <card number> <amount> to stack cards.")
        await msg.edit(embed=embed)

        running = True
        while running:
            try:
                self.submit_callback(self.ctx, interaction=True)
                command, user = await self.bot.wait_for(
                    'encounter_command',
                    timeout=30,
                    check=lambda c, u: u.id == self.ctx.author.id
                )
                if command.name == "stack":
                    key = command.args[0] - 1
                    if key in range(5):
                        resp, details = deck.stack(key, command.args[1])
                        if details is not None:
                            await self.ctx.send(
                                f"**Success!** You stacked {details[0].name} {command.args[1]} times! Your deck is now:\n"
                                f"{deck.show_cards}"
                            )
                        else:
                            if resp == 0:
                                await self.ctx.send(
                                    "**Oops!** You dont have enough identical cards to stack that many!\n")
                            elif resp == -1:
                                await self.ctx.send(
                                    "**Oops!** You have already ready up'd your cards. Time to attack!\n")
                elif command.name == "attack":
                    if len(deck.attacks) <= 0:
                        await self.ctx.send("You haven't stacked any cards to attack with!")
                    else:
                        msg = await self.ctx.send("*You attack!* Rolling attacks...")
                        new_content = await self._apply_attack(deck)
                        await msg.edit(content=new_content)
                        await asyncio.sleep(1)
                        running = False
            except asyncio.TimeoutError:
                return -1

    async def _apply_attack(self, deck: Deck):
        await asyncio.sleep(1)

        total_damage = 0
        rolls = []
        for i, attack in enumerate(deck.attacks):
            character = attack[0]
            roll_to_hit = character.roll_attack()
            if roll_to_hit >= self.monster.ac:
                multiplier = len(attack)
                damage = character.roll_damage() * multiplier
                deck.character_xp_area[character.id] += (damage * 5)
                rolls.append(f"`⚔️• Attack {i + 1}, rolled {roll_to_hit}, Damage {damage}.` **HIT!**\n")
                total_damage += damage
            else:
                rolls.append(f"`⚔️• Attack {i + 1}, rolled {roll_to_hit}.` **MISS!**\n")

        self.monster.hp -= total_damage
        msg = f"**You launch {len(deck.attacks)} attacks! - AC to beat: {self.monster.ac}**\n" \
              f"You deal a total of {total_damage} damage!\n"
        msg += "".join(rolls)
        msg += "\n\u200b"
        return msg

    async def monster_turn(self):
        msg = await self.ctx.send("It's the monster's turn get ready to roll saves!")
        await asyncio.sleep(2)

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
    async def process_commands_internally(cls, command: str, args: list) -> PartialCommand:
        return PartialCommand(command, *args)
