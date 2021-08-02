import json

import discord

from data.database import MongoDatabase

SETTINGS_PATH = 'default_settings.json'


class Settings:
    with open(SETTINGS_PATH, 'r') as file:
        settings = json.load(file)


class GuildConfig:
    """
        Object representing a guild's custom settings, this system can
        be modified to expand settings as an when they are needed (relies on Settings Class).
        This also handles all DB interactions and self contains it.
        :returns GuildConfig object:
    """

    def __init__(self, guild_id, database):
        """
        :param guild_id:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        On creation the class calls the data getting the guild settings
        if prefix is None it reverts back to `-`, this should never happen
        under normal circumstances.
        Premium by default is False and will default to False in case of
        failure.
        """
        self.guild_id = guild_id
        self._db = database
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


class GuildWebhooks:
    def __init__(self, guild_id, database=None):
        """
        :param guild_id:
        :param database: -> Optional
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        On creation the class calls the data getting the guild webhooks
        this includes News and Release webhooks
        """
        self.guild_id = guild_id
        self._db = db if database is None else database
        self.data = self._db.get_guild_webhooks(guild_id=guild_id)
        self.news = self.data['news']
        self.release = self.data['release']

    def add_webhook(self, webhook: discord.Webhook, feed_type: str):
        if feed_type == "releases":
            self.release = webhook.url
        elif feed_type == "news":
            self.news = webhook.url
        else:
            raise NotImplementedError("No webhook option for {} type".format(feed_type))
        self._db.set_guild_webhooks(self.guild_id, self.to_dict())

    def delete_webhook(self, feed_type: str):
        if feed_type == "releases":
            self.release = None
        elif feed_type == "news":
            self.news = None
        else:
            raise NotImplementedError("No webhook option for {} type".format(feed_type))
        if self.news is None and self.release is None:
            self._db.delete_guild_webhooks(guild_id=self.guild_id)
        else:
            self._db.set_guild_webhooks(self.guild_id, self.to_dict())

    def to_dict(self):
        return {'user_id': self.guild_id,
                'news': self.news,
                'release': self.release
                }


if __name__ == "__main__":
    db = MongoDatabase()
