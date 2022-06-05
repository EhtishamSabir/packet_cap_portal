from pathlib import Path
from flask import Flask, render_template, request, make_response, flash, redirect
from packet_processor import process_file, start_capture_into_flie, stop_capture, refresh, live_stats, get_devices, \
    deleteall
import threading
from datetime import datetime
from config_data import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER SECRET'


@app.route('/', methods=['GET'])
def home():
    username = request.cookies.get('username')
    if username:
        # return render_template('home.html', username=username)
        return redirect("/devices")
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.cookies.get('username')
    if username:
        return render_template('login.html', username=username)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            flash("Successful login", "success")
            resp = make_response(redirect('/'))
            resp.set_cookie('username', username)
            return resp
        else:
            flash("Wrong username or password", "danger")
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp


@app.route('/devices', methods=['GET'])
def devices():
    final_results = get_devices()

    username = request.cookies.get('username')
    if username:
        return render_template('home.html',
                               username=username,
                               final_results=final_results)


@app.route('/captured', methods=['GET'])
def get_files(pth='/captured', ext=".pcapng"):
    pth = Path(pth)
    files_path = []
    for each_file in list(filter(lambda y: y.is_file(), pth.iterdir())):
        if each_file.suffix == ext:
            files_path.append(each_file.__str__())
    return {"files": files_path}


@app.route('/process_file', methods=['GET'])
def cap_file_queue():
    global files_in_queue
    try:
        filenames = request.get_json(force=True)['files']
    except:
        return {"queue": files_in_queue}
    print(filenames)
    if filenames is None:
        print("it's none")
        return {"queue": files_in_queue}
    for each_file in filenames:
        if each_file in files_in_queue:
            filenames.remove(each_file)
    files_in_queue = files_in_queue + filenames
    syn_config()
    return {"queue": files_in_queue, "processing": len(processing), "processed": processed_files}


@app.route('/start_processing', methods=['GET'])
def process_cap_file():
    for filename in files_in_queue:
        print("file in queue")
        t = threading.Thread(target=process_file, args=(filename,))
        t.start()
        processing.append({"file": filename, "time": datetime.now().__str__(), "info": t})
        files_in_queue.remove(filename)

    for process in processing:
        if not process['info'].is_alive():
            processing.remove(process)
            processed_files.append(process['file'])
    CONFIG_DATA['files_in_queue'] = files_in_queue
    CONFIG_DATA.sync()
    syn_config()
    return {"processed": processed_files,
            "processing": [len(processing), [x['file'] + "|" + x['time'] for x in processing]],
            "queue": files_in_queue}


@app.route('/start_livecapture', methods=['GET'])
def start_livecapture():
    interface_id = request.args.get('interface_id')
    try:
        interface_id = int(interface_id)
    except TypeError:
        return "not valid ID"
    return start_capture_into_flie(f"today{interface_id}", str(interface_id))


@app.route('/stop_capture', methods=['GET'])
def stop_livecapture():
    interface_id = request.args.get('interface_id')
    return stop_capture(str(interface_id))


@app.route('/stats', methods=['GET'])
def get_stats():
    return live_stats()


@app.route('/stats', methods=['GET'])
def refresh_tshark():
    global interval
    int_val = request.args.get('interval')
    if int_val:
        interval = str(int_val)
    refresh()
    return {"status": "complete"}


@app.route('/deleteall', methods=['GET'])
def delete_files():
    global interval
    int_val = request.args.get('all')
    if int_val:
        deleteall(sure=True)
    else:
        deleteall()
    return {"status": "complete"}


app.run(host='0.0.0.0', port=88, debug=True)
