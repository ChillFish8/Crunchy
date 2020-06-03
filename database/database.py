import pymongo
import json
from logger import Logger


class Settings:
    with open('default_settings.json', 'r') as file:
        settings = json.load(file)


class GuildData:
    """ Custom Guild settings """

    def __init__(self, db):
        self.db = db
        self.guild_configs = self.db["guilds"]

    def set_guild_config(self, guild_id: int, config: dict) -> [dict, int]:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        Logger.log_database("SET-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data))

        if current_data is not None:
            QUERY = {'_id': guild_id}
            new_data = {'config': config}
            resp = self.guild_configs.update_one(QUERY, {'$set': new_data})
            return resp.raw_result
        else:
            data = {'_id': guild_id, 'config': config}
            resp = self.guild_configs.insert_one(data)
            return resp.inserted_id

    def reset_guild_config(self, guild_id: int):
        current_data = self.guild_configs.find_one_and_delete({'_id': guild_id})
        Logger.log_database(
            "DELETE-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data))
        return "COMPLETE"

    def get_guild_config(self, guild_id: int) -> dict:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        return current_data['config'] if current_data is not None else Settings.settings


class GuildWebhooks:
    """ Custom Guild settings """

    def __init__(self, db):
        self.db = db
        self.guild_configs = self.db["guilds"]

    def set_guild_webhooks(self, guild_id: int, config: dict) -> [dict, int]:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        Logger.log_database("SET-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data))

        if current_data is not None:
            QUERY = {'_id': guild_id}
            new_data = {'config': config}
            resp = self.guild_configs.update_one(QUERY, {'$set': new_data})
            return resp.raw_result
        else:
            data = {'_id': guild_id, 'config': config}
            resp = self.guild_configs.insert_one(data)
            return resp.inserted_id

    def reset_guild_config(self, guild_id: int):
        current_data = self.guild_configs.find_one_and_delete({'_id': guild_id})
        Logger.log_database(
            "DELETE-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data))
        return "COMPLETE"

    def get_guild_config(self, guild_id: int) -> dict:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        return current_data['config'] if current_data is not None else {'news': None,
                                                                        'release':
                                                                            {
                                                                                'mention': [],
                                                                                'url': None
                                                                            }
                                                                        }


class UserTracking:
    """ User's Watchlist, Recommended etc... """

    def __init__(self, db):
        self.db = db
        self.collections = {
            "favourites": self.db["favouritelist"],
            "watchlist": self.db["watchlist"],
            "recommended": self.db["recommendedlist"],
        }

    def set_user_data(self, area: str, user_id: int, contents: list) -> [dict, int]:
        current_data = self.collections[area].find_one({'_id': user_id})
        Logger.log_database("SET-USER: User Content with Id: {} returned.".format(user_id))

        if current_data is not None:
            QUERY = {'_id': user_id}
            new_data = {'contents': contents}
            resp = self.collections[area].update_one(QUERY, {'$set': new_data})
            return resp.raw_result
        else:
            data = {'_id': user_id, 'contents': contents}
            resp = self.collections[area].insert_one(data)
            return resp.inserted_id

    def reset_user_data(self, area: str, user_id: int):
        _ = self.collections[area].find_one_and_delete({'_id': user_id})
        Logger.log_database(
            "DELETE-USER: Guild with Id: {} returned.".format(user_id))
        return "COMPLETE"

    def get_user_data(self, area: str, user_id: int) -> list:
        current_data = self.collections[area].find_one({'_id': user_id})
        if area == "recommended":
            return current_data['contents'] if current_data is not None else {
                'public': True,
                'list': [],
                'blocked': [],
                'bypass': []}
        else:
            return current_data['contents'] if current_data is not None else []


class MongoDatabase(GuildData, UserTracking, GuildWebhooks):
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
        self.collections = {
            "favourites": self.db["favouritelist"],
            "watchlist": self.db["watchlist"],
            "recommended": self.db["recommendedlist"],
        }
        super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the database """
        self.db.logout()


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
        self.nsfw_enabled = data.pop('nsfw_enabled', True)  # Emergency safe guard

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

    def toggle_nsfw(self):
        self.nsfw_enabled = not self.nsfw_enabled
        self._db.set_guild_config(self.guild_id, config=self.to_dict())
        return self.nsfw_enabled

    def to_dict(self):
        return {
            'prefix': self.prefix,
            'premium': self.premium,
            'nsfw_enabled': self.nsfw_enabled,
        }


class BasicTracker:
    """
        Object representing a users's items to be tracked, this system can
        be modified to expand settings as an when they are needed.
        This also handles all DB interactions and self contains it.
        :returns BasicTracker object:
    """

    def __init__(self, user_id, type_, database=None):
        """
        :param database: -> Optional
        If database is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        """
        self.user_id = user_id
        self.type = type_
        self._db = db if database is None else database
        self._contents = self._db.get_user_data(area=self.type, user_id=user_id)

    def add_content(self, data: dict):
        self._contents.append(data)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)
        return self._contents

    def remove_content(self, index: int):
        self._contents.pop(index)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)
        return self._contents

    def _generate_block(self):
        """ This turns a list of X amount of side into 10 block chunks. """
        pages, rem = divmod(len(self._contents), 10)
        chunks, i = [], 0
        for i in range(0, pages, 10):
            chunks.append(self._contents[i:i + 10])
        if rem != 0:
            chunks.append(self._contents[i:i + rem])
        return chunks

    def get_blocks(self):
        """ A generator to allow the bot to paginate large sets. """
        for block in self._generate_block():
            yield block

    @property
    def amount_of_items(self):
        return len(self._contents)

    def to_dict(self):
        return {'content': self._contents}


class UserFavourites(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="favourites", database=database)


class UserWatchlist(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="watchlist", database=database)


class UserRecommended(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="recommended", database=database)

    @property
    def is_public(self):
        return self._contents['public']

    def is_bypass(self, id_):
        return id_ in self._contents['bypass']

    def is_blocked(self, id_):
        return id_ in self._contents['blocked']

    def block(self, id_):
        if id_ in self._contents['bypass']:
            self._contents['bypass'].remove(id_)
        if id_ not in self._contents['blocked']:
            self._contents['blocked'].append(id_)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)

    def bypass(self, id_):
        if id_ in self._contents['blocked']:
            self._contents['blocked'].remove(id_)
        if id_ not in self._contents['bypass']:
            self._contents['bypass'].append(id_)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)

    def toggle_public(self):
        self._contents['public'] = not self._contents['public']
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)
        return self._contents['public']

    def add_content(self, data: dict):
        self._contents['list'].append(data)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)
        return self._contents['list']

    def remove_content(self, index: int):
        self._contents['list'].pop(index)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents=self._contents)
        return self._contents['list']

    def _generate_block(self):
        """ This turns a list of X amount of side into 10 block chunks. """
        pages, rem = divmod(len(self._contents['list']), 10)
        chunks, i = [], 0
        for i in range(0, pages, 10):
            chunks.append(self._contents['list'][i:i + 10])
        if rem != 0:
            chunks.append(self._contents['list'][i:i + rem])
        return chunks

    def get_blocks(self):
        """ A generator to allow the bot to paginate large sets. """
        for block in self._generate_block():
            yield block

    @property
    def amount_of_items(self):
        return len(self._contents['list'])

    def to_dict(self):
        return {'content': self._contents}


if __name__ == "__main__":
    db = MongoDatabase()
