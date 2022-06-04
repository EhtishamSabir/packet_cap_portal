import pymongo
import pyshark
from operator import attrgetter
from db_helper import get_client
import os, re, signal
from time import sleep
from datetime import datetime
import subprocess
from config_data import *


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


def get_devices(test=True):
    if test:
        return '''1. ciscodump (Cisco remote capture)
2. dpauxmon (DisplayPort AUX channel monitor capture)
3. randpkt (Random packet generator)
4. sdjournal (systemd Journal Export)
5. sshdump (SSH remote capture)
6. udpdump (UDP Listener remote capture)
'''

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
    print('runing file ', filename)
    sleep(10 * 1)
    print("file is finished")
    return

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
    return


def start_capture_into_flie(filename, interface, interval_seconds):
    global process_queue
    # live capture example
    if interface not in capture_processing['interface']:
        print("start")
        p = subprocess.Popen(f'tshark -i {interface} -b interval:{interval_seconds} -w /captured/{filename}.pcapng',
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
    for pid in queue[interface]['process']:
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
    except subprocess.CalledProcessError:
        return
    return


def get_devices():
    return subprocess.check_output('tshark -D', shell=True).decode('utf-8')


if __name__ == '__main__':
    start_capture_into_flie("today", '1', '10')
