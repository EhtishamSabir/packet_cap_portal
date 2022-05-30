from flask import Flask, render_template, request, make_response, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER SECRET'

@app.route('/', methods = ['GET'])
def home():
    username = request.cookies.get('username')
    if username:
        return render_template('home.html', username=username)
    return render_template('home.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    username = request.cookies.get('username')
    if username:
        return render_template('login.html', username=username)
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username=='admin' and password=='admin':
            flash("Successful login", "success")
            resp = make_response(redirect('/'))
            resp.set_cookie('username', username)
            return resp
        else:
            flash("Wrong username or password", "danger")
    return render_template('login.html')

@app.route('/logout', methods = ['GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp
app.run(host='0.0.0.0', port=80,debug=True)