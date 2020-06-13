from data.database import MongoDatabase


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
        If data is None it falls back to a global var,
        THIS ONLY EXISTS WHEN RUNNING THE FILE AS MAIN!
        """
        self.user_id = user_id
        self.type = type_
        self._db = db if database is None else database
        self.data = self._db.get_user_data(area=self.type, user_id=user_id)
        self._contents = self.data.get("contents", [])
        self.public = self.data.get("firewall", True)

    def add_content(self, data: dict):
        self._contents.append(data)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents={'contents': self._contents,
                                                                               'firewall': self.public})
        return self._contents

    def remove_content(self, index: int):
        temp = self._contents.pop(index)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents={'contents': self._contents,
                                                                               'firewall': self.public})
        return temp

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

    def toggle_public(self):
        self.public = not self.public
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents={'contents': self._contents,
                                                                               'firewall': self.public})
        return self.public

    @property
    def is_public(self):
        return self.public


class UserFavourites(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="favourites", database=database)


class UserWatchlist(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="watchlist", database=database)


class UserRecommended(BasicTracker):
    def __init__(self, user_id, database=None):
        super().__init__(user_id, type_="recommended", database=database)

    def add_content(self, data: dict):
        self._contents.append(data)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents={'contents': self._contents,
                                                                               'firewall': self.public})
        return self._contents

    def remove_content(self, index: int):
        deleted = self._contents.pop(index)
        self._db.set_user_data(area=self.type, user_id=self.user_id, contents={'contents': self._contents,
                                                                               'firewall': self.public})
        return deleted


if __name__ == "__main__":
    db = MongoDatabase()
