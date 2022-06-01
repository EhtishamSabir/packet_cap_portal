import os
import re
from pathlib import Path
from flask import Flask, render_template, request, make_response, flash, redirect
from packet_processor import process_file
import threading
from datetime import datetime

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
def devices(test=True):
    if test:
        final_results = [
            {
                "IP": "_gateway",
                "LAN_IP": "10.255.255.254",
                "MAC_ADDRESS": "00:10:db:ff:10:01"
            },
            {
                "IP": "?",
                "LAN_IP": "172.18.0.2",
                "MAC_ADDRESS": "02:42:ac:12:00:02"
            },
            {
                "IP": "?",
                "LAN_IP": "10.255.255.101",
                "MAC_ADDRESS": "70:4c:a5:81:38:78"
            }
        ]
    else:
        full_results = [re.findall('^[\w\?\.]+|(?<=\s)\([\d\.]+\)|(?<=at\s)[\w\:]+', i) for i in os.popen('arp -a')]
        final_results = [dict(zip(['IP', 'LAN_IP', 'MAC_ADDRESS'], i)) for i in full_results]
        final_results = [{**i, **{'LAN_IP': i['LAN_IP'][1:-1]}} for i in final_results]

    username = request.cookies.get('username')
    if username:
        return render_template('home.html',
                               username=username,
                               final_results=final_results)


@app.route('/captured', methods=['GET'])
def get_files(pth='./captured', ext=".pcapng"):
    pth = Path(pth)
    files_path = []
    for each_file in list(filter(lambda y: y.is_file(), pth.iterdir())):
        if each_file.suffix == ext:
            files_path.append(each_file)
    return files_path


files_in_queue = []
processed_files = []
processing = []


@app.route('/process_file', methods=['GET'])
def cap_file_queue():
    filename = request.args.get('filename')
    if filename is None:
        print("it's none")
        return {"queue": files_in_queue}
    if filename in files_in_queue:
        print("already in queue")
    elif filename not in processed_files and filename not in [x['file'] for x in processing]:
        files_in_queue.append(filename)
    return {"queue": files_in_queue}


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

    return {"processed": processed_files,
            "processing": [len(processing), [x['file'] + "|" + x['time'] for x in processing]],
            "queue": files_in_queue}


app.run(host='0.0.0.0', port=80, debug=True)
