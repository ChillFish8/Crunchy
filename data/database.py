import json

import pymongo

from logger import Logger, Timer


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
        Logger.log_database(
            "SET-GUILD: Guild with Id: {} returned with results: {}".format(guild_id, current_data))
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
            "DELETE-GUILD: Guild with Id: {} returned with results: {}".format(guild_id,
                                                                               current_data))
        return "COMPLETE"

    def get_guild_config(self, guild_id: int) -> dict:
        current_data = self.guild_configs.find_one({'_id': guild_id})
        Logger.log_database("GET-GUILD: User Content with Id: {} returned.".format(guild_id))
        return current_data['config'] if current_data is not None else Settings.settings


class GuildWebhooks:
    """ Custom Guild webhooks """

    def __init__(self, db):
        self.db = db
        self.guild_web_hooks = self.db["webhooks"]

    @Timer.timeit
    def set_guild_webhooks(self, guild_id: int, config: dict) -> [dict, int]:
        current_data = self.guild_web_hooks.find_one(
            {'_id': "{guild_id}".format(guild_id=guild_id)})
        Logger.log_database(
            "SET-WEBHOOK: Guild with Id: {} returned with results: {}".format(guild_id, None))
        if current_data is not None:
            QUERY = {'_id': f"{guild_id}"}
            new_data = {'config': config}
            resp = self.guild_web_hooks.update_one(QUERY, {'$set': new_data})
            return resp.raw_result
        else:
            data = {'_id': f"{guild_id}", 'config': config}
            resp = self.guild_web_hooks.insert_one(data)
            return resp.inserted_id

    @Timer.timeit
    def delete_guild_webhooks(self, guild_id: int):
        _ = self.guild_web_hooks.find_one_and_delete(
            {'_id': "{guild_id}".format(guild_id=guild_id)})
        Logger.log_database(
            "DELETE-WEBHOOK: Guild with Id: {} returned with results: {}".format(guild_id, None))
        return "COMPLETE"

    @Timer.timeit
    def get_guild_webhooks(self, guild_id: int) -> dict:
        current_data = self.guild_web_hooks.find_one(
            {'_id': "{guild_id}".format(guild_id=guild_id)})
        return current_data['config'] if current_data is not None else {'user_id': guild_id,
                                                                        'news': None,
                                                                        'release': None
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

    def set_user_data(self, area: str, user_id: int, contents: dict) -> [dict, int]:
        current_data = self.collections[area].find_one({'_id': user_id})
        Logger.log_database("SET-USER: User Content with Id: {} returned.".format(user_id))

        if current_data is not None:
            QUERY = {'_id': user_id}
            resp = self.collections[area].update_one(QUERY, {'$set': contents})
            return resp.raw_result
        else:
            data = {'_id': user_id, **contents}
            resp = self.collections[area].insert_one(data)
            return resp.inserted_id

    def reset_user_data(self, area: str, user_id: int):
        _ = self.collections[area].find_one_and_delete({'_id': user_id})
        Logger.log_database(
            "DELETE-USER: Guild with Id: {} returned.".format(user_id))
        return "COMPLETE"

    def get_user_data(self, area: str, user_id: int) -> dict:
        current_data = self.collections[area].find_one({'_id': user_id})
        return current_data if current_data is not None else {'_id': user_id, 'firewall': True,
                                                              'contents': []}


class Votes:
    """ Tracking on vote events for rewards"""

    def __init__(self, db):
        self.db = db
        self.votes: pymongo.collection.Collection = self.db['votes']

    def get_vote(self, user_id):
        returned = self.votes.find_one({'_id': f"{user_id}"})
        Logger.log_database("GET-VOTE: User Content with Id: {} returned.".format(user_id))
        return returned if returned is not None else {'user_id': user_id, 'expires_in': None}

    def add_vote(self, user_id, expires_in):
        self.votes.insert_one({'_id': f"{user_id}", 'expires_in': expires_in})
        Logger.log_database("SET-VOTE: User Content with Id: {} returned.".format(user_id))

    def update_vote(self, user_id, expires_in):
        self.votes.find_one_and_update({'_id': f"{user_id}"}, {'$set': {'expires_in': expires_in}})
        Logger.log_database("SET-VOTE: User Content with Id: {} returned.".format(user_id))

    def remove_vote(self, user_id):
        self.votes.find_one_and_delete({'_id': f"{user_id}"})
        Logger.log_database("DELETE-VOTE: User Content with Id: {} returned.".format(user_id))

    def remove_outdated(self, time_secs):
        return self.votes.delete_many({'expires_in': {'$lte': time_secs}}).deleted_count


class MongoDatabase(GuildData, UserTracking, GuildWebhooks, Votes):
    """
        This is the main Mongo DB class, this pull data from config.json and
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
        print(
            f"Connected to {addr}:{port} from {self.client.HOST}, Version: {version}, Git Version: {git_ver}")

        self.db = self.client["Crunchy"]
        self.collections = {
            "favourites": self.db["favouritelist"],
            "watchlist": self.db["watchlist"],
            "recommended": self.db["recommendedlist"],
        }
        self.guild_web_hooks = self.db["webhooks"]
        self.votes = self.db['votes']
        super().__init__(self.db)

    def close_conn(self):
        """ Logs us out of the data """
        self.db.logout()


if __name__ == "__main__":
    db = MongoDatabase()
