class EventsStore:
    def __init__(self, db):
        self._db = db
        self.events = self._db["event_channels"]

    def update_event(self, guild_id: int, **kwargs):
        if self.events.find_one({'_id': guild_id}) is not None:
            return self.events.find_one_and_update({'_id': guild_id}, {'$set': kwargs})
        else:
            return self.events.insert_one({'_id': guild_id}, **kwargs)

    def delete_event(self, guild_id: int):
        return self.events.find_one_and_delete({'_id': guild_id})

    def get_all_events(self):
        return list(self.events.find())
