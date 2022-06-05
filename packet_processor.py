import pymongo
import pyshark
from operator import attrgetter
from db_helper import get_client
import os, re
from time import sleep
from datetime import datetime
import subprocess
from config_data import *


def get_attrb(pth, packet, default=None):
    try:
        return attrgetter(pth)(packet)
    except AttributeError:
        return default


def get_devices():
    return subprocess.check_output("tshark -D", shell=True).decode('utf')


# parser
def packet_parser(packet, options):
    dct = {}
    for path in options:
        ikey = '.'.join(path.lower().strip().split('.'))
        dct[ikey] = get_attrb(ikey, packet)
    return dct


def feilds():
    with open('fields', 'r') as f:
        return list(f.readlines())


def process_file(filename):
    # add check if file exists

    options = feilds

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
    return {"completed": "true"}


def start_capture_into_flie(filename, interface):
    global process_queue
    # live capture example
    if interface not in capture_processing['interface']:
        print("start")
        p = subprocess.Popen(f'tshark -i {interface} -b interval:{interval} -w /captured/{filename}.pcapng',
                             shell=True)
        o = subprocess.check_output(f"ps -ax | grep tshark", shell=True).decode("utf-8")
        print(o)

        i_queue = []
        for p in [p.split(' ')[1] for p in o.splitlines() if '-c ps -ax' not in p]:
            if p not in process_queue:
                i_queue.append(p)
        process_queue = process_queue + i_queue
        queue[interface] = {"process": i_queue}

        print(queue)
        print(process_queue)
        capture_processing['interface'].append(interface)
    syn_config()
    return capture_processing


def stop_capture(interface):
    global process_queue
    try:
        process = queue[interface]['process']
    except KeyError:
        return {"queue": queue}
    for pid in process:
        print("trying to stop", pid, ":::")
        try:
            o = subprocess.check_output(f"kill -9 {pid}", shell=True).decode("utf-8")
            print(o)
            process_queue = list(set(process_queue))
            process_queue.remove(pid)
        except subprocess.CalledProcessError:
            print("process not found")
        except KeyError:
            print("process queue pop error")
    if queue:
        print(queue)
        queue.pop(interface)
        capture_processing['interface'].remove(interface)
    syn_config()
    return {"queue": queue}


def live_stats():
    return {"queue": queue}


def refresh():
    try:
        subprocess.check_output("pkill tshark", shell=True)
        process_queue.clear()
        processed_files.clear()
        process_queue.clear()
    except subprocess.CalledProcessError:
        return
    syn_config()
    return


def deleteall(sure=False):
    try:

        if sure:
            refresh()
            subprocess.check_output("rm -r /captured ", shell=True)
            subprocess.check_output("mkdir /captured ", shell=True)
        else:
            for file in processed_files:
                os.remove(file)
            processed_files.clear()
    except subprocess.CalledProcessError:
        return
    syn_config()
    return


def get_devices():
    resp = subprocess.check_output('tshark -D', shell=True).decode('utf-8')
    return {"devices": ['.'.join(x.split('.')[1:]) for x in resp.splitlines()]}


if __name__ == '__main__':
    start_capture_into_flie("today", '1', '10')
