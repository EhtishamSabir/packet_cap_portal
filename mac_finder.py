import pymongo
import requests
from time import sleep

from db_helper import get_unique_mac, get_client


def get_mac_info(mac_addr):
    url = "https://mac-address-lookup1.p.rapidapi.com/static_rapid/mac_lookup/"

    querystring = {"query": mac_addr}

    headers = {
        "X-RapidAPI-Host": "mac-address-lookup1.p.rapidapi.com",
        "X-RapidAPI-Key": "fc12865c2bmsh3bed2ea92a875b6p146116jsn48300b649277"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.json())
    return response.json()


def save_mac(db, macs, tag='src'):
    for mac in macs:
        print(mac)
        res = db.mac_info.find({'_id': mac})
        try:
            print(res[0]['data'])
            if res[0]['data']['message']:
                pass
            else:
                continue
        except IndexError:
            pass
        except KeyError:
            continue
        print('waiting 3 seconds', sleep(3))
        resp = get_mac_info(mac)

        try:
            if resp['message']:
                continue
        except KeyError:
            pass

        try:
            db.mac_info.insert_one({'_id': mac,
                                    "data": resp})
        except pymongo.errors.DuplicateKeyError:
            db.mac_info.replace_one({'_id': mac}, {'_id': mac,
                                                   "data": resp})


def device_capture():
    db = get_client()
    macs = get_unique_mac(isrc=False)
    save_mac(db, macs, tag='src')
    macs = get_unique_mac()
    save_mac(db, macs, tag='dst')
    return


def get_devices():
    db = get_client()
    return list(db.mac_info.find({}))
