import pymongo
import pyshark
from operator import attrgetter
from db_helper import get_client
import os, re
from time import sleep


def get_attrb(pth, packet, default=None):
    try:
        return attrgetter(pth)(packet)
    except AttributeError:
        return default


def get_devices_ip_mac(test=True):
    if test:
        return [{'IP': '_gateway', 'LAN_IP': '10.255.255.254', 'MAC_ADDRESS': '00:10:db:ff:10:01'},
                {'IP': '?', 'LAN_IP': '172.18.0.2', 'MAC_ADDRESS': '02:42:ac:12:00:02'},
                {'IP': '?', 'LAN_IP': '10.255.255.101', 'MAC_ADDRESS': '70:4c:a5:81:38:78'}]
    full_results = [re.findall('^[\w\?\.]+|(?<=\s)\([\d\.]+\)|(?<=at\s)[\w\:]+', i) for i in os.popen('arp -a')]
    final_results = [dict(zip(['IP', 'LAN_IP', 'MAC_ADDRESS'], i)) for i in full_results]
    final_results = [{**i, **{'LAN_IP': i['LAN_IP'][1:-1]}} for i in final_results]
    return final_results


# parser
def packet_parser(packet, options):
    dct = {}
    for path in options:
        ikey = '.'.join(path.lower().strip().split('.'))
        dct[ikey] = get_attrb(ikey, packet)
    return dct


def process_file(filename):
    print('runing file ',filename)
    sleep(10 * 1)
    print("file is finished")
    return


    with open('fields', 'r') as f:
        options = f.readlines()

    # reading captured file
    cap = pyshark.FileCapture(filename)

    # live capture example
    # cap = pyshark.LiveCapture(display_filter="tcp.port == 80")
    db = get_client()

    try:
        resp_list = []
        for i, packet in enumerate(cap):
            resp = packet_parser(packet, options)
            resp['_id'] = resp['frame_info.number']
            resp_list.append(resp)
            if i % 1000 == 0:
                print("adding to DB 1000s entries")
                try:
                    db.fields_collection.insert_many(resp_list, ordered=False)
                except pymongo.errors.BulkWriteError:
                    pass
                resp_list.clear()
    except OSError:
        print("processing finished.")
    return
