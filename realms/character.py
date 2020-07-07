import random
import json
import time

from utils.id_maker import get_id

BASE_HEARTS = 5
BASE_FOOD = 5
BASE_TREATS = 5

class CharacterRef:
    with open(r"resources/archieve/main_characters.json", "r") as file:
        references = json.load(file)

    @classmethod
    def get_character(cls, name):
        for character in cls.references:
            if character['name'].lower() == name.lower():
                return character


class Character:
    def __init__(self, name=None, icon=None):
        self.name = name
        self.icon = icon
        self.id = get_id()

        self.modifiers = {}
        self._level = 1
        self._hp = random.randint(45, 70)

    def _unload_self(self) -> dict:
        items = self.__dict__
        export = {}
        for key, value in items.items():
            export[key] = value
        return export

    def to_dict(self) -> dict:
        return self._unload_self()

    def from_dict(self, character_dict: dict):
        for key, value in character_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    @property
    def level(self):
        return self._level

    @property
    def stat_block(self):
        return f"• STR 12 (+2), • DEX 16 (+5), • CON 12 (+2), • INT 16 (+3), • WIS 10 (-2), • CHA 18 (+4)"

    @property
    def hp(self):
        return self._hp
