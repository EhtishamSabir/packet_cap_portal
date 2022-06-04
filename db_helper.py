import pymongo
from pymongo import MongoClient
import dns.resolver


def get_client():
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8']
    client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
    if 'packets_filter' not in client.list_database_names():
        db = client.get_database('packets_filter')
    else:
        db = client.packets_filter
    if 'config_data' not in db.list_collection_names():
        db.create_collection('config_data')
    if 'fields_collection' not in db.list_collection_names():
        db.create_collection('fields_collection')
    return db


def get_config(data=None):
    db = get_client()
    if data:
        try:
            db.config_data.insert_one({'_id': "default",
                                       "data": data})
        except pymongo.errors.DuplicateKeyError:
            db.config_data.replace_one({'_id': "default"}, {'_id': "default",
                                                            "data": data})
    try:
        return db.config_data.find({'_id': 'default'})[0]['data']
    except IndexError:
        return {}


print(get_config())
