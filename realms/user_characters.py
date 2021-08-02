import time
from datetime import timedelta
from typing import Optional

from realms.character import Character
from realms.datastores.database import MongoDatabase


class UserCharacters:
    """
        Object representing a user's characters, this system can
        be modified to expand to fit anything that is needed which
        will likely be the case as this system is developed.
        This also handles all DB interactions and self contains it.
        :returns UserCharacters object:
    """

    def __init__(self, user_id, database, rolls=None, callback=None):
        """
        :param user_id:
        :param rolls:
        :param callback:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        """
        self.user_id = user_id
        self._db: MongoDatabase = database
        self._redis = self._db.redis

        data = self._db.get_characters(user_id=user_id)

        self.characters = data.pop('characters', [])  # Emergency safe guard
        self.rank = data.pop('rank', {'ranking': 0, 'power': 0, 'total_character': 0})
        self.bank = data.pop('balance', {'copper': 50, 'gold': 10, 'platinum': 0})
        self._rolls = rolls
        # self._expires_in = data.pop('expires_in', expires_in)
        self.mod_callback = callback

    def update_on_db(self):
        self._db.update_any(self.user_id, characters=self.characters, rank=self.rank,
                            balance=self.bank)

    def submit_character(self, character: Character):
        if self._db.characters.find_one({'_id': self.user_id}) is not None:
            self.characters.append(character.to_dict())
            self._db.update_characters(self.user_id, self.characters)
        else:
            self.characters.append(character.to_dict())
            self._db.add_characters(self.user_id,
                                    {'characters': self.characters, 'rank': self.rank,
                                     'balance': self.bank})

    def dump_character(self, character: Character):
        id_ = character.id
        for i, character_ in enumerate(self.characters):
            if character_['id'] == id_:
                self.characters.pop(i)
        if len(self.characters) > 0:
            self._db.update_characters(self.user_id, self.characters)
        else:
            self._db.reset_characters(user_id=self.user_id)
        return self.characters

    def get_character(self, search: str = None, id_: int = None) -> [dict, None]:
        for character in self.characters:
            if search is not None:
                if character['name'].lower() == search.lower():
                    return character
            elif id_ is not None:
                if character['id'] == id_:
                    return character
        if search is not None:
            for character in self.characters:
                if search.lower() in character['name'].lower():
                    return character
        return None

    def update_character(self, character: Character) -> Character:
        for i, char in enumerate(self.characters):
            if character.id == char['id']:
                self.characters[i] = character.to_dict()
        self._db.update_characters(self.user_id, self.characters)
        return character

    def update_rolls(self, modifier: int):
        self._rolls += modifier
        if self.rolls_left <= 0:
            offset = timedelta(hours=12)
            await self._redis.set(self.cache_key, time.time() + offset.total_seconds(), ex=offset)
        self.mod_callback(self.user_id, self)

    @property
    def rolls_left(self):
        return self._rolls

    @property
    def cache_key(self):
        return f"characters:timeouts_{self.user_id}"

    @property
    def expires_in(self) -> Optional[timedelta]:
        val = await self._redis.get(self.cache_key)
        if val is None:
            return None

        return timedelta(seconds=int(val))

    def get_blocks(self):
        """ A generator to allow the bot to paginate large sets. """
        for i in range(0, len(self.characters), 5):
            yield self.characters[i:i + 5]

    @property
    def amount_of_items(self):
        return len(self.characters)

    def update_balance(self, platinum=0, gold=0, copper=0):
        self.bank['platinum'] += platinum
        self.bank['gold'] += gold
        self.bank['copper'] += copper
        self._db.update_any(self.user_id, characters=self.characters, rank=self.rank,
                            balance=self.bank)
        return self.bank

    @property
    def platinum(self):
        return self.bank['platinum']

    @property
    def gold(self):
        return self.bank['gold']

    @property
    def copper(self):
        return self.bank['copper']
