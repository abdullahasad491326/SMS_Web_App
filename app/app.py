from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import requests
import database  # This is your database.py file

app = Flask(__name__)
app.secret_key = 'your_secret_key'
limiter = Limiter(get_remote_address, app=app)

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
        if database.get_user(phone):
            flash("❌ User already exists.")
        else:
            database.add_user(phone, password)
            flash("✅ Account created successfully!")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = database.get_user(phone)
        if user and user[1] == password:
            session['user'] = phone
            flash("✅ Login successful.")
            return redirect('/dashboard')
        else:
            flash("❌ Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    phone = session['user']
    user = database.get_user(phone)

    if request.method == 'POST':
        if database.is_blocked(phone):
            flash("🚫 You are blocked from sending SMS.")
        elif user[2] <= 0:
            flash("💸 Not enough coins.")
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
            try:
                res = requests.post("https://api.crownone.app/api/v1/Registration/verifysms",
                                    json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    database.decrement_coin(phone)
                    database.add_sms_log(phone, to, message)
                    flash("✅ Message sent successfully.")
                else:
                    flash("❌ Error sending SMS.")
            except Exception as e:
                flash(f"⚠️ Failed to send SMS: {str(e)}")

    user = database.get_user(phone)
    return render_template('dashboard.html', coins=user[2])

@app.route('/logout')
def logout():
    session.clear()
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
            flash("❌ Invalid admin credentials")
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
            if database.get_user(phone):
                database.add_coins(phone, coins)
                flash(f"✅ Added {coins} coins to {phone}")
            else:
                flash("❌ User not found.")
        elif action == "block":
            database.block_user(phone)
            flash(f"🚫 Blocked user {phone}")
        elif action == "unblock":
            database.unblock_user(phone)
            flash(f"✅ Unblocked user {phone}")

    users = database.get_all_users()
    logs = database.get_all_logs()
    blocked = database.get_all_blocked()
    return render_template('admin_panel.html', users=users, logs=logs, blocked=blocked)

if __name__ == "__main__":
    app.run(debug=True)
