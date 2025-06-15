from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

limiter = Limiter(app, key_func=get_remote_address)

# File-based "database"
DATA_FILE = 'users.json'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '2113576AABBCCDD'

# Load users
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if phone in users:
            return render_template('register.html', message='User already registered.')
        if password != confirm:
            return render_template('register.html', message='Passwords do not match.')

        users[phone] = {
            'password': password,
            'coins': 0,
            'blocked': False,
            'logs': []
        }
        save_users(users)
        flash("Registration successful! You can now login.")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if phone in users and users[phone]['password'] == password:
            if users[phone].get('blocked'):
                return render_template('login.html', message='You are blocked.')
            session['user'] = phone
            return redirect('/dashboard')
        else:
            return render_template('login.html', message='Invalid credentials.')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    phone = session['user']
    if request.method == 'POST':
        number = request.form['number']
        message = request.form['message']
        if users[phone]['coins'] <= 0:
            return render_template('dashboard.html', phone=phone, coins=users[phone]['coins'], message="Not enough coins.")
        
        # Simulated API request (you can replace with real API)
        import requests
        try:
            res = requests.post("https://api.crownone.app/api/v1/Registration/verifysms", json={
                "Code": 1234,
                "Mobile": number,
                "Message": message
            })
            if res.status_code == 200:
                users[phone]['coins'] -= 1
                users[phone]['logs'].append({
                    'number': number,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                save_users(users)
                return render_template('dashboard.html', phone=phone, coins=users[phone]['coins'], message="SMS sent successfully!")
            else:
                return render_template('dashboard.html', phone=phone, coins=users[phone]['coins'], message="Failed to send SMS.")
        except:
            return render_template('dashboard.html', phone=phone, coins=users[phone]['coins'], message="API error.")
    return render_template('dashboard.html', phone=phone, coins=users[phone]['coins'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin_panel')
        else:
            return render_template('admin_login.html', message='Invalid admin credentials.')
    return render_template('admin_login.html')

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin_login')
    users = load_users()
    return render_template('admin_panel.html', users=[
        {'phone': k, **v} for k, v in users.items()
    ])

@app.route('/add_coins', methods=['POST'])
def add_coins():
    if not session.get('admin'):
        return redirect('/admin_login')
    phone = request.form['phone']
    coins = int(request.form['coins'])
    users = load_users()
    if phone in users:
        users[phone]['coins'] += coins
        save_users(users)
    return redirect('/admin_panel')

@app.route('/toggle_block', methods=['POST'])
def toggle_block():
    if not session.get('admin'):
        return redirect('/admin_login')
    phone = request.form['phone']
    users = load_users()
    if phone in users:
        users[phone]['blocked'] = not users[phone].get('blocked', False)
        save_users(users)
    return redirect('/admin_panel')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin_login')

if __name__ == '__main__':
    app.run(debug=True)
