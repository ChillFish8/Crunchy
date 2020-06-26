import json
import pymongo


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
        self.characters = self.db["collected_characters"]
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

    def update_any(self, user_id: int, **kwargs):
        if self.characters.find_one({'_id': user_id}) is not None:
            return self.characters.find_one_and_update({'_id': user_id}, {'$set': kwargs})
        else:
            return self.characters.insert_one({'_id': user_id}, **kwargs)

    def update_characters(self, user_id: int, characters: list):
        return self.characters.find_one_and_update({'_id': user_id}, {'$set': {'characters': characters}})

    def add_characters(self, user_id: int, data: dict):
        self.characters.insert_one({'_id': user_id, **data})

    def update_rank(self, user_id: int, rank: dict):
        return self.characters.find_one_and_update({'_id': user_id}, {'$set': {'rank': rank}})

    def reset_characters(self, user_id: int):
        return self.characters.find_one_and_delete({'_id': user_id})
