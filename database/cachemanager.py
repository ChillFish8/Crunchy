from datetime import datetime, timedelta


class Store:
    def __init__(self, name: str, max_time: timedelta=timedelta(minutes=15)):
        self.name = name
        self.store = {}
        self._temp = {}
        self.max_time = max_time

    def get(self, _id):
        return self.store.get(_id, None)

    def store(self, _id, _object):
        self.store[_id] = _object

    def clear(self):
        self.store = {}

    def check(self, item):
        if (datetime.now() - item[1]['entered']) > self.max_time:
            return False
        else:
            return item

    def apply(self, item):
        self._temp[item[0]] = item[1]
        return item

    def clean(self):
        all_entries = self.store.items()
        new = tuple(filter(self.check, all_entries))
        map(self.apply, new)
        self.store = self._temp

    def __str__(self):
        return self.name


class CacheManager:
    def __init__(self):
        self.collections = {}

    def add_cache_store(self, cache_collection: Store):
        self.collections[str(cache_collection)] = cache_collection

    def reset_cache_store(self, collection_name: str):
        collection: Store = self.collections[collection_name]
        replacement = Store(name=collection.name, max_time=collection.max_time)
        self.collections[collection_name] = replacement

    def remove_cache_store(self, collection_name: str) -> [Store, None]:
        return self.collections.pop(collection_name, None)

    def get(self, collection_name: str, _id):
        return self.collections[collection_name].get(_id=_id)

    def store(self, collection_name: str, _id, data):
        self.collections[collection_name].store(_id=_id, _object=data)
