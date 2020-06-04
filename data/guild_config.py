import json
from data.database import MongoDatabase


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
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        On creation the class calls the data getting the guild settings
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

if __name__ == "__main__":
    db = MongoDatabase()
