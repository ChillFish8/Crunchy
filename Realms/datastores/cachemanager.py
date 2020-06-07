from datetime import datetime, timedelta
import asyncio
from logger import Logger

class Store:
    def __init__(self, name: str, max_time: timedelta=timedelta(minutes=15)):
        self.name = name
        self._cache = {}
        self._temp = {}
        self.max_time = max_time

    def get(self, _id):
        resp = self._cache.get(_id, None)
        if resp is not None:
            data = resp['data']
            self.store(_id=_id, _object=data)
            return data
        else:
            return resp

    def store(self, _id, _object):
        self._cache[_id] = {'entered': datetime.now(), 'data': _object}

    def clear(self):
        self._cache = {}

    def check(self, item):
        if (datetime.now() - item[1]['entered']) > self.max_time:
            return False
        else:
            return item

    def clean(self):
        all_entries = self._cache.items()
        new = list(filter(self.check, all_entries))
        self._cache = dict(new)

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

    async def background_task(self):
        while True:
            for key in self.collections:
                self.collections[key].clean()
                Logger.log_cache("[ BACKGROUND TASK ] | Cleaned up cache {}!".format(key))
            await asyncio.sleep(10)
