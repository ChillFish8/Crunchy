import random
import json
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
    def __init__(self, name=None, icon=None, base_power=None, defense=None, attack=None):
        self.name = name
        self.icon = icon
        self.id = get_id()
        self.modifiers = {}

        self._base_power = base_power
        self._base_defense = defense
        self._base_attack = attack

        self._hearts = 3
        self._food = 5
        self._treat = 5

    def _unload_self(self) -> dict:
        items = self.__dict__
        export = {}
        for key, value in items.items():
            if not isinstance(value, object):
                export[key] = value
        return export

    def _load_unknown(self):
        if any([item is None for item in [self._base_power, self._base_defense, self._base_attack]]):
            ref = CharacterRef.get_character(self.name)
            if ref is None:
                raise ValueError("No Character reference for this character!")

            self._base_power = self._base_power if self._base_power is not None else ref['base_power']
            self._base_defense = self._base_defense if self._base_defense is not None else ref['defense']
            self._base_attack = self._base_attack if self._base_attack is not None else ref['attack']

    def to_dict(self) -> dict:
        return self._unload_self()

    def from_dict(self, character_dict: dict):
        for key, value in character_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def render_modifiers(self):
        string = ""
        for key, value in self.modifiers.items():
            string += f"• {key} - `{value}`\n"
        return string if string != "" else "No Mods"

    def render_character_info(self):
        hearts = "💔" * BASE_HEARTS
        hearts = f"**[ Hearts ]** `{hearts.replace('💔', '❤️', self.hearts)}`\n"

        food = " " * BASE_HEARTS
        food = f"**[ Food & Drink ]** `{food.replace(' ', '🍔', self.food)}`\n"

        treats = " " * BASE_HEARTS
        treats = f"**[ Treats ]** `{treats.replace(' ', '🍬', self.treat)}`\n"
        return f"{hearts}\n{food}\n{treats}\n"

    @property
    def power(self) -> int:
        if self._base_power is None:
            self._load_unknown()
        export_power = 0
        for key, value in self.modifiers.items():
            mod = value.get("num_modifier", "0")
            if mod.startswith("-"):
                export_power - int(mod[1:])
            elif mod.startswith("+"):
                export_power + int(mod[1:])
        export_power += self._base_power
        return export_power

    @property
    def attack(self):
        return self._base_attack

    @property
    def defense(self):
        return self._base_defense

    @property
    def hearts(self):
        return self._hearts

    @property
    def food(self):
        return self._food

    @property
    def treat(self):
        return self._treat


