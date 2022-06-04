import os
from db_helper import get_config

path = '/captured'
# Check whether the specified path exists or not
isExist = os.path.exists(path)
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(path)
    print("The new directory is created!")

CONFIG_DATA = get_config()
files_in_queue = []
processed_files = []
processing = []
capture_processing = {'interface': []}
queue = {}
process_queue = []

try:
    files_in_queue = CONFIG_DATA['files_in_queue']
    processed_files = CONFIG_DATA['processed_files']
    processing = CONFIG_DATA['processing']

    capture_processing = CONFIG_DATA['capture_processing']
    queue = CONFIG_DATA['queue']
    process_queue = CONFIG_DATA['process_queue']

except KeyError:
    CONFIG_DATA['files_in_queue'] = []
    CONFIG_DATA['processed_files'] = []
    CONFIG_DATA['processing'] = []
    CONFIG_DATA['capture_processing'] = {'interface': []}
    CONFIG_DATA['queue'] = {}
    CONFIG_DATA['process_queue'] = []


def syn_config():
    CONFIG_DATA['files_in_queue'] = files_in_queue
    CONFIG_DATA['processed_files'] = processed_files
    CONFIG_DATA['processing'] = processing
    CONFIG_DATA['capture_processing'] = capture_processing
    CONFIG_DATA['queue'] = queue
    CONFIG_DATA['process_queue'] = process_queue
    print(CONFIG_DATA)
    get_config(CONFIG_DATA)
    return
