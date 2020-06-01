import pymongo
import json
from logger import Logger


class Settings:
    with open('default_settings.json', 'r') as file:
        settings = json.load(file)


class GuildConfig:
    """
        Object representing a guild's custom settings, this system can
        be modified to expand settings as an when they are needed (relies on Settings Class).
        This also handles all DB interactions and self contains it.
        :returns GuildConfig object:
    """

    def __init__(self, guild_id, database=None):
        """
        :param guild_id:
        :param database: -> Optional
        If database is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        On creation the class calls the database getting the guild settings
        if prefix is None it reverts back to `-`, this should never happen
        under normal circumstances.
        Premium by default is False and will default to False in case of
        failure.
        """
        self.guild_id = guild_id
        self._db = db if database is None else database
        data = self._db.get_guild_config(guild_id=guild_id)

        self.prefix = data.pop('prefix', '-')  # Emergency safe guard
        self.premium = data.pop('premium', False)  # Emergency safe guard

    def set_prefix(self, new_prefix) -> str:
        """
        This function sets it's own attr to the new prefix then
        calls the db setting the new prefix from it's attr to avoid desync
        :returns prefix:
        """
        self.prefix = new_prefix
        self._db.set_guild_config(self.guild_id, config=self.to_dict())
        return self.prefix

    def reset_prefix(self) -> str:
        """
        resets guild config on db.
        :returns default_prefix:
        """
        self.prefix = Settings.settings.get('prefix', '-')
        self._db.set_guild_config(self.guild_id, config=self.to_dict())
        return self.prefix

    def to_dict(self):
        return {
            'prefix': self.prefix,
            'premium': self.premium
        }


class MongoDatabase:
    """
        This is the main Mongo DB class, this pull data from config.json and
        connects to the remote mongoDB (Falls back to local host if config missing)
        + Class Inherits:
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
        super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the database """
        self.db.logout()


class GuildData:
    """ Custom Guild settings """

    def __init__(self, db):
        self.db = db
        self.guild_configs = self.db["guilds"]

    def set_guild_config(self, guild_id: int, config: dict) -> [dict, int]:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        "SET-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data)

        if current_data is not None:
            QUERY = {'_id': guild_id}
            new_data = {'config': config}
            resp = self.guild_configs.update_one(QUERY, {'$set': new_data})
            "Data updated area with GuildId: {},\n" \
                "      resp: {}\n".format(guild_id, resp.raw_result)
            return resp.raw_result
        else:
            data = {'_id': guild_id, 'config': config}
            resp = self.guild_configs.insert_one(data)
            "Data inserted into area with GuildId: {},\n" \
                "      resp: {}\n".format(guild_id, {'_id': resp.inserted_id, 'complete': resp.acknowledged})
            return resp.inserted_id

    def reset_guild_config(self, guild_id: int):
        current_data = self.guild_configs.find_one_and_delete({'_id': guild_id})
        "DELETE-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data)
        return "COMPLETE"

    def get_guild_config(self, guild_id: int) -> dict:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        return current_data['config'] if current_data is not None else Settings.settings


if __name__ == "__main__":
    db = MongoDatabase()
