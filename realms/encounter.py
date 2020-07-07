import discord
import asyncio

from random import randint
from discord.ext import commands

from realms.parties import Party
from realms.generation.monsters import MonsterManual, Monster

class Encounter:
    def __init__(self, bot, ctx, party: Party):
        self.bot = bot
        self.ctx = ctx
        self.party = party
        self.monster_manual = MonsterManual()
        self.monster = None

    def get_rand_monster(self):
        cr = randint(self.party.challenge_rating - 2, self.party.challenge_rating + 5)
        monster = self.monster_manual.get_random_monster(cr)
        return monster

    async def menu(self):
        random_monsters = [self.get_rand_monster() for _ in range(4)]
        print(random_monsters)

    async def battle(self):
        pass

