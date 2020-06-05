import random
from utils.id_maker import get_id

class Character:
    def __init__(self, name=None, icon=None):
        self.name = name
        self.icon = icon
        self.id = get_id()
        self._base_power = random.randint(0, 64)
        self._defense = random.randint(0, 10)
        self._attack = random.randint(0, 10)
        self.modifiers = {}

    def _unload_self(self) -> dict:
        items = self.__dict__
        export = {}
        for key, value in items.items():
            if not key.startswith("_") or not isinstance(value, object):
                export[key] = value
        return export

    def to_dict(self) -> dict:
        return self._unload_self()

    def from_dict(self, character_dict: dict):
        for key, value in character_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError("Unknown value present in loading.")
        return self

    @property
    def power(self) -> int:
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
        return self._attack

    @property
    def defense(self):
        return self._defense
