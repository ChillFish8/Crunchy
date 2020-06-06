import json
import random
import discord

from datetime import datetime
from discord.ext import commands
from discord.ext import tasks

from realms.character import Character
from realms.user_characters import UserCharacters, MongoDatabase
from utils.paginator import Paginator

NON_VOTE_ROLLS = 15
VOTE_ROLLS_MOD = +25
RANDOM_EMOJIS = ['💞', '💗', '💖', '💓']
DEFAULT = {
    'messages': []
}

HAPPY_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784208075915274/exitment.png",
    "https://cdn.discordapp.com/attachments/680350705038393344/717784643117777006/wow.png"
]
SAD_URL = [
    "https://cdn.discordapp.com/attachments/680350705038393344/717784461391167568/sad.png",
]


def filter_(item_content):
    if item_content[1].get_time_obj() is None:
        return {item_content[0]: item_content[1]}
    elif item_content[1].get_time_obj() < datetime.now():
        return False
    else:
        return {item_content[0]: item_content[1]}


class CharacterGets(commands.Cog):
    with open(r"resources/archieve/main_characters.json", "r") as file:
        RANDOM_CHARACTERS = json.load(file)
    random.shuffle(RANDOM_CHARACTERS)
    group = RANDOM_CHARACTERS[:5000]
    database = MongoDatabase()

    def __init__(self, bot):
        self.bot = bot
        self.cool_down_checks = {}
        self.pending = {}
        self.remove_null.start()
        self.shuffle.start()

    def callback(self, user_id, user_characters: UserCharacters):
        self.cool_down_checks[user_id] = user_characters

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        data['user'] = int(data['user'])
        if data['user'] in self.cool_down_checks:
            if self.cool_down_checks['user'].get_time_obj() is None:
                self.cool_down_checks['user'].update_rolls(+25)
            else:
                del self.cool_down_checks['user']

    @tasks.loop(seconds=10)
    async def remove_null(self):
        self.cool_down_checks = dict(
            filter(filter_, self.cool_down_checks.items()))

    @tasks.loop(minutes=30)
    async def shuffle(self):
        random.shuffle(self.RANDOM_CHARACTERS)
        self.group = self.RANDOM_CHARACTERS[:5000]

    @commands.command(aliases=['c'])
    async def character(self, ctx):
        user_characters: UserCharacters = self.bot.cache.get('characters', ctx.author.id)
        if user_characters is None:
            user: UserCharacters = self.cool_down_checks.get(ctx.author.id, None)
            if user is not None:
                rolls = user.rolls_left
            else:
                if ctx.has_voted(user_id=ctx.author.id):
                    rolls = NON_VOTE_ROLLS + VOTE_ROLLS_MOD
                else:
                    rolls = NON_VOTE_ROLLS
            user_characters = UserCharacters(user_id=ctx.author.id,
                                             database=self.database,
                                             rolls=rolls,
                                             expires_in=self.cool_down_checks.get('expires_in', None),
                                             callback=self.callback)
            self.bot.cache.store('characters', ctx.author.id, user_characters)

        if not Checks.has_rolls(user_characters):
            if not ctx.has_voted(user_id=ctx.author.id):
                return await ctx.send("<:HimeSad:676087829557936149> Oops! You dont have any more rolls left,"
                                      " upvote Crunchy to get more rolls and other awesome perks!\n"
                                      "https://top.gg/bot/656598065532239892/vote")
            else:
                return await ctx.send(f"<:HimeSad:676087829557936149> Oops! You dont have any more rolls left,"
                                      f" come back in {user_characters.expires_in} hours when ive found some more characters!")

        c = random.choice(self.group)
        character_obj = Character(name=c['name'],
                                  icon=c['url'],
                                  base_power=c['base_power'],
                                  defense=c['defense'],
                                  attack=c['attack'])
        embed = discord.Embed(
            title=character_obj.name,
            description=f"💪 **Power:** `{character_obj.power}`\n"
                        f"⚔️ **Attack:** `{character_obj.attack}`\n"
                        f"🛡️ **Defense:** `{character_obj.defense}`\n",
            color=self.bot.colour)
        embed.set_image(url=character_obj.icon)
        embed.set_footer(text=f"You have {user_characters.rolls_left} rolls left!")
        message = await ctx.send(embed=embed)
        user_characters.update_rolls(modifier=-1)
        await self.submit_wait_for(message, character_obj, user_characters, ctx.author, ctx.channel)

    async def submit_wait_for(self, message: discord.Message,
                              character_obj: Character,
                              user_character_obj: UserCharacters,
                              user_obj: discord.User,
                              channel: discord.TextChannel):
        await message.add_reaction(random.choice(RANDOM_EMOJIS))
        payload = {
            'character': character_obj,
            'user_character': user_character_obj,
            'message_id': message.id,
            'user': user_obj,
            'channel': channel
        }
        user = self.pending.get(user_character_obj.user_id, DEFAULT)
        user['messages'].append(payload)
        self.pending[user_character_obj.user_id] = user

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.pending.get(payload.user_id, False):
            for pending in self.pending[payload.user_id]['messages']:
                if pending['message_id'] == payload.message_id:
                    if str(payload.emoji) in RANDOM_EMOJIS:
                        pending['user_character'].submit_character(pending['character'])
                        await pending['channel'].send(
                            f"<:HimeHappy:677852789074034691> <@{pending['user'].id}> "
                            f"chose {pending['character'].name}! Good job!")
                        break

    async def generate_embeds(self, user: discord.User, area):
        pages, rem = divmod(area.amount_of_items, 10)
        if rem != 0:
            pages += 1

        embeds = []
        for i, chunk in enumerate(area.get_blocks()):
            embed = discord.Embed(color=self.bot.colour, timestamp=datetime.now())\
                .set_footer(text=f"Page {i + 1} / {pages}")
            for x, item in enumerate(chunk):
                embed.add_field(value=f"** {x + i*10 + 1} ) - {item['name']}**",
                                name="\u200b",
                                inline=False)
            embed.set_thumbnail(url=random.choice(HAPPY_URL))
            embed.set_author(name=f"{user.name}'s collected characters", icon_url=user.avatar_url)
            embeds.append(embed)
        return embeds

    @commands.command(name="viewcharacters", aliases=['characters'])
    async def my_characters(self, ctx, user: discord.User=None):
        if user is not None:
            user_ = user
            user_characters: UserCharacters = self.bot.cache.get('characters', user.id)
            if user_characters is None:
                rolls = self.cool_down_checks.get('rolls_left', NON_VOTE_ROLLS)
                user_characters = UserCharacters(user_id=user.id,
                                                 database=self.database,
                                                 rolls=rolls,
                                                 expires_in=self.cool_down_checks.get('expires_in', None),
                                                 callback=self.callback)
                self.bot.cache.store('characters', user.id, user_characters)
        else:
            user_ = ctx.author
            user_characters: UserCharacters = self.bot.cache.get('characters', ctx.author.id)
            if user_characters is None:
                rolls = self.cool_down_checks.get('rolls_left', NON_VOTE_ROLLS)
                if ctx.has_voted(user_id=ctx.author.id):
                    rolls += 25
                user_characters = UserCharacters(user_id=ctx.author.id,
                                                 database=self.database,
                                                 rolls=rolls,
                                                 expires_in=self.cool_down_checks.get('expires_in', None),
                                                 callback=self.callback)
                self.bot.cache.store('characters', ctx.author.id, user_characters)

        if user_characters.amount_of_items <= 0:
            embed = discord.Embed(color=self.bot.colour) \
                .set_footer(text="Hint: Vote for Crunchy on top.gg to get more perks!")
            embed.description = f"Oops! {'You' if user is None else 'They'} dont " \
                                f"have any collected characters,\n lets get them filling list!"
            embed.set_thumbnail(url=random.choice(SAD_URL))
            embed.set_author(name=f"{user_.name}'s collected characters", icon_url=user_.avatar_url)
            return await ctx.send(embed=embed)
        else:
            embeds = await self.generate_embeds(user=user_, area=user_characters)
            if len(embeds) > 1:
                pager = Paginator(embed_list=embeds,
                                  bot=self.bot,
                                  message=ctx.message,
                                  colour=self.bot.colour)
                return self.bot.loop.create_task(pager.start())
            else:
                return await ctx.send(embed=embeds[0])

    @classmethod
    def shutdown(cls):
        cls.database.close_conn()

class Checks:
    @classmethod
    def has_rolls(cls, user: UserCharacters):
        return user.rolls_left > 0


def setup(bot):
    bot.add_cog(CharacterGets(bot))

def teardown(bot):
    CharacterGets.shutdown()

