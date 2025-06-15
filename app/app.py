from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = '24113576AABBCCDD'

limiter = Limiter(app, key_func=get_remote_address)

users = {}
sms_logs = []
blocked_users = []

ADMIN_USER = "PAKCYBER"
ADMIN_PASS = "24113576"

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if phone in users:
            flash("User already exists.")
        else:
            users[phone] = {'password': password, 'coins': 5}
            flash("Account created!")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if phone in users and users[phone]['password'] == password:
            session['user'] = phone
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    phone = session['user']
    user_data = users.get(phone, {})
    if request.method == 'POST':
        if phone in blocked_users:
            flash("You are blocked from sending SMS.")
        elif user_data['coins'] <= 0:
            flash("Insufficient coins.")
        else:
            to = request.form['to']
            message = request.form['message']
            payload = {
                "Code": 1234,
                "Mobile": to,
                "Message": message
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "user-agent": "okhttp/4.9.2"
            }
            response = requests.post("https://api.crownone.app/api/v1/Registration/verifysms",
                                     json=payload, headers=headers)
            users[phone]['coins'] -= 1
            sms_logs.append({'user': phone, 'to': to, 'message': message, 'time': datetime.now()})
            flash("Message sent successfully.")
    return render_template('dashboard.html', coins=user_data.get('coins', 0))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = username
            return redirect('/admin_panel')
        else:
            flash("Invalid admin credentials")
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin_login')
    if request.method == 'POST':
        action = request.form['action']
        phone = request.form['phone']
        if action == "add":
            coins = int(request.form['coins'])
            if phone in users:
                users[phone]['coins'] += coins
        elif action == "block":
            if phone not in blocked_users:
                blocked_users.append(phone)
        elif action == "unblock":
            if phone in blocked_users:
                blocked_users.remove(phone)
    return render_template('admin_panel.html', users=users, logs=sms_logs, blocked=blocked_users)

if __name__ == "__main__":
    app.run(debug=True)
