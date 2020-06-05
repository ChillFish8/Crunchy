import json
import pymongo

from datetime import datetime, timedelta

from realms.character import Character


class MongoDatabase:
    """
        This is the character system only Mongo DB class, this pull data from config.json and
        connects to the remote mongoDB (Falls back to local host if config missing)
        + Class Inherits:
            - GuildData
            - UserTracking
            - GuildWebhooks
        """

    with open(r'database_config.json', 'r') as file:
        config = json.load(file)

    def __init__(self):
        """
        This method requires no parameters, It takes all data from the
        class var `config`, if data is missing from config it falls
        back to the following settings:
        + host: localhost
        + port: 27017
        + user: root
        + password: root
        """

        addr = self.config.get('host_address', 'localhost')
        port = self.config.get('port', '27017')
        usr = self.config.get('username', 'root')
        pas = self.config.get('password', 'root')
        host = f"mongodb://{usr}:{pas}@{addr}:{port}/"

        self.client = pymongo.MongoClient(host)
        system_info = self.client.server_info()
        version = system_info['version']
        git_ver = system_info['gitVersion']
        print(f"Connected to {addr}:{port} from {self.client.HOST}, Version: {version}, Git Version: {git_ver}")

        self.db = self.client["Crunchy"]
        self.characters = self.db["characters"]
        # super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the data """
        self.db.logout()

    def get_characters(self, user_id: int):
        resp = self.characters.find_one({'_id': user_id})
        return resp if resp is not None else {
            '_id': user_id,
            'characters': [],
            'rank': {'ranking': 0, 'power': 0, 'total_character': 0}
        }

    def update_characters(self, user_id: int, characters: list):    
        return self.characters.find_one_and_update({'_id': user_id}, {'$set': {'characters': characters}})

    def add_characters(self, user_id: int, data: dict):
        self.characters.insert_one({'_id': user_id, **data})

    def update_rank(self, user_id: int, rank: dict):
        return self.characters.find_one_and_update({'_id': user_id}, {'$set': {'rank': rank}})

    def reset_characters(self, user_id: int):
        return self.characters.find_one_and_delete({'_id': user_id})


class UserCharacters:
    """
        Object representing a user's characters, this system can
        be modified to expand to fit anything that is needed which
        will likely be the case as this system is developed.
        This also handles all DB interactions and self contains it.
        :returns UserCharacters object:
    """

    def __init__(self, user_id, rolls, expires_in, callback, database=None):
        """
        :param user_id:
        :param rolls:
        :param callback:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        """
        self.user_id = user_id
        self._db = db if database is None else database
        data = self._db.get_characters(user_id=user_id)

        self.characters = data.pop('characters', [])  # Emergency safe guard
        self.rank = data.pop('rank', {'ranking': 0, 'power': 0, 'total_character': 0})
        self._rolls = rolls
        self._expires_in = expires_in
        self.mod_callback = callback

    def submit_character(self, character: Character):
        if len(self.characters) > 0:
            self.characters.append(character.to_dict())
            self._db.update_characters(self.user_id, self.characters)
        else:
            self.characters.append(character.to_dict())
            self._db.add_characters(self.user_id,
                                    {'characters': self.characters, 'rank': self.rank})

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

    def update_rolls(self, modifier: int):
        self._rolls += modifier
        if self.rolls_left <= 0:
            self._expires_in = datetime.now() + timedelta(hours=12)
        self.mod_callback(self.user_id, self)

    @property
    def rolls_left(self):
        return self._rolls

    def get_time_obj(self):
        return self._expires_in

    @property
    def expires_in(self):
        if self._expires_in is not None:
            hours, seconds = divmod(self._expires_in.total_seconds(), 3600)
            minutes, seconds = divmod(seconds, 60)
            return f"{hours}h, {minutes}m, {seconds}s"
        return self._expires_in

    def _generate_block(self):
        """ This turns a list of X amount of side into 10 block chunks. """
        pages, rem = divmod(len(self.characters), 10)
        chunks, i = [], 0
        for i in range(0, pages, 10):
            chunks.append(self.characters[i:i + 10])
        if rem != 0:
            chunks.append(self.characters[i:i + rem])
        return chunks

    def get_blocks(self):
        """ A generator to allow the bot to paginate large sets. """
        for block in self._generate_block():
            yield block

    @property
    def amount_of_items(self):
        return len(self.characters)


if __name__ == "__main__":
    db = MongoDatabase()
