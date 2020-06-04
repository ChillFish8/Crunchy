import json
import pymongo

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
        super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the data """
        self.db.logout()

    def get_characters(self, user_id: int):
        return self.characters.find_one({'_id': user_id})

    def update_characters(self, user_id: int, characters: list):
        return self.characters.find_one_and_update({'_id': user_id}, {'characters': characters})

    def update_rank(self, user_id: int, rank: dict):
        return self.characters.find_one_and_update({'_id': user_id}, {'rank': rank})

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

    def __init__(self, user_id, database=None):
        """
        :param user_id:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        """
        self.user_id = user_id
        self._db = db if database is None else database
        data = self._db.get_guild_config(guild_id=user_id)

        self.characters = data.pop('characters', [])  # Emergency safe guard
        self.rank = data.pop('rank', {'ranking': 0, 'power': 0, 'total_character': 0})

    def submit_character(self, character: Character):
        self.characters.append(character.to_dict())
        self._db.update_characters(self.user_id, self.characters)

    def dump_character(self, character: Character):

if __name__ == "__main__":
    db = MongoDatabase()
