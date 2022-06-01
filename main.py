import os
import re
from pathlib import Path
from flask import Flask, render_template, request, make_response, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER SECRET'


@app.route('/', methods=['GET'])
def home():
    username = request.cookies.get('username')
    if username:
        return render_template('home.html', username=username)
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
        return [{'IP': '_gateway', 'LAN_IP': '10.255.255.254', 'MAC_ADDRESS': '00:10:db:ff:10:01'},
                {'IP': '?', 'LAN_IP': '172.18.0.2', 'MAC_ADDRESS': '02:42:ac:12:00:02'},
                {'IP': '?', 'LAN_IP': '10.255.255.101', 'MAC_ADDRESS': '70:4c:a5:81:38:78'}]
    full_results = [re.findall('^[\w\?\.]+|(?<=\s)\([\d\.]+\)|(?<=at\s)[\w\:]+', i) for i in os.popen('arp -a')]
    final_results = [dict(zip(['IP', 'LAN_IP', 'MAC_ADDRESS'], i)) for i in full_results]
    final_results = [{**i, **{'LAN_IP': i['LAN_IP'][1:-1]}} for i in final_results]

    return final_results


@app.route('/captured', methods=['GET'])
def get_files(pth='./captured', ext=".pcapng"):
    pth = Path(pth)
    files_path = []
    for each_file in list(filter(lambda y: y.is_file(), pth.iterdir())):
        if each_file.suffix == ext:
            files_path.append(each_file)
    return files_path


app.run(host='0.0.0.0', port=80, debug=True)
