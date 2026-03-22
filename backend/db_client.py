import pymongo
from django.conf import settings

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        cfg = settings.MONGODB_SETTINGS
        kwargs = {
            'host': cfg['HOST'],
            'port': cfg['PORT'],
        }
        if cfg.get('USERNAME'):
            kwargs['username'] = cfg['USERNAME']
            kwargs['password'] = cfg['PASSWORD']
            kwargs['authSource'] = cfg.get('AUTH_SOURCE', 'admin')
        _client = pymongo.MongoClient(**kwargs)
        _db = _client[cfg['DB_NAME']]
    return _db


def get_collection(name: str):
    return get_db()[name]
