from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

limiter = Limiter(get_remote_address, app=app)

# In-memory "database"
users = {}
messages = []
blocked_users = set()

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
            return redirect('/register')
        users[phone] = {'password': password, 'coins': 5, 'blocked': False}
        flash("Successfully registered!")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = users.get(phone)
        if user and user['password'] == password:
            if user['blocked']:
                flash("You are blocked.")
                return redirect('/login')
            session['user'] = phone
            return redirect('/dashboard')
        flash("Invalid login.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=get_remote_address)
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    user = users.get(session['user'])
    if user['blocked']:
        flash("You are blocked.")
        return redirect('/login')

    if request.method == 'POST':
        number = request.form['number']
        message = request.form['message']

        if user['coins'] <= 0:
            flash("Not enough coins.")
            return redirect('/dashboard')

        # Send SMS using backend API (Termux-style)
        payload = {
            "Code": 1234,
            "Mobile": number,
            "Message": message
        }
        headers = {
            "Host": "api.crownone.app",
            "accept": "application/json",
            "content-type": "application/json",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2"
        }
        try:
            res = requests.post("https://api.crownone.app/api/v1/Registration/verifysms", 
                                data=json.dumps(payload), headers=headers)
            if res.status_code == 200:
                user['coins'] -= 1
                messages.append({
                    'user': session['user'],
                    'number': number,
                    'message': message,
                    'time': request.date
                })
                flash("SMS sent successfully!")
            else:
                flash("Failed to send SMS.")
        except Exception as e:
            flash(f"Error: {str(e)}")

    return render_template('dashboard.html', coins=user['coins'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- Admin Area ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == "PAKCYBER" and request.form['password'] == "24113576":
            session['admin'] = True
            return redirect('/admin_panel')
        flash("Invalid admin credentials")
    return render_template("admin_login.html")

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':
        phone = request.form.get('phone')
        coins = int(request.form.get('coins', 0))
        action = request.form.get('action')

        if phone in users:
            if action == 'block':
                users[phone]['blocked'] = True
            elif action == 'unblock':
                users[phone]['blocked'] = False
            elif action == 'add_coins':
                users[phone]['coins'] += coins
        else:
            flash("User not found")

    return render_template('admin_panel.html', users=users, messages=messages)

# -------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
