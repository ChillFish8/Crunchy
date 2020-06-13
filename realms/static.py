from datetime import timedelta

from realms.datastores.database import MongoDatabase
from realms.datastores.cachemanager import CacheManager, Store


REQUIRED_CACHE = [
    ['top_global', timedelta(hours=1)],
    ['top_guild', timedelta(hours=1)],
    ['top_user_guild', timedelta(hours=1)],
]


class Database:
    db = MongoDatabase()
    cache = CacheManager()
    for collection in REQUIRED_CACHE:
        cache.add_cache_store(Store(name=collection[0], max_time=collection[1]))
