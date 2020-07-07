import random
import json


class MonsterManual:
    def __init__(self):
        with open(r'realms/generation/monster_name.json', 'r') as file:
            self.random_names = json.load(file)

    async def get_random_monster(self, challenge_rating):
        pass