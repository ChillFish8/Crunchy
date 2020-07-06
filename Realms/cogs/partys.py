import discord

from discord.ext import commands

from realms.user_characters import UserCharacters
from realms.datastores.database import MongoDatabase
from realms.static import Database


class Party:
    def __init__(self, bot, ctx: commands.Context, user_area: UserCharacters, **options):
        self.bot = bot
        self.ctx = ctx
        self.user_area = user_area
        self._page_no = 0
        self._selected_party =

    @staticmethod
    def format_characters(chars: list, target_pos: int=0):
        texts = []
        current = "\u200b"
        for i, character in enumerate(chars):
            if i+1 % 5 == 0:
                texts.append(current)
                current = ""

            if i == target_pos:
                current += "<:index:705013516850954290> "
            current += f"{i + 1}) {character['name']} (Level {character['level']})\n"
        return texts

    def generate_embed(self):
        embed = discord.Embed(color=self.bot.colour)
        embed.set_author(name=f"{self.ctx.author.name}'s Party", icon_url=self.ctx.author.avatar_url)

        chars = self.user_area.characters[self._page_no * 10: self._page_no + 10]
        sections = self.format_characters(chars)

        # Character Lists
        embed.add_field(name="Characters | 1", value=sections[0])
        embed.add_field(name="Characters | 2", value=sections[1])

        selected = f""
        embed.add_field(name="Selected Characters", value="", inline=False)

class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def make_select_embed(self, ctx: commands.Context, user_area: UserCharacters, page_no: int, **options):



    @commands.command(name="selectparty", aliases=['setparty'])
    async def select_party(self, ctx: commands.Context):
        user_area = UserCharacters(ctx.author.id, Database.db)
        pass

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
