from flask import Flask, render_template, request, redirect, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import requests
import database

app = Flask(__name__)
app.secret_key = 'your_secret_key'

limiter = Limiter(get_remote_address, app=app)

ADMIN_USER = "PAKCYBER"
ADMIN_PASS = "24113576"

# Initialize database tables
database.init_db()

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
            database.create_user(phone, password)
            flash("✅ Account created successfully!")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = database.get_user(phone)
        if user and user['password'] == password:
            session['user'] = phone
            flash("✅ Login successful.")
            return redirect('/dashboard')
        else:
            flash("❌ Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    phone = session['user']
    user = database.get_user(phone)
    blocked = database.is_blocked(phone)

    if request.method == 'POST':
        if blocked:
            flash("🚫 You are blocked from sending SMS.")
        elif user['coins'] <= 0:
            flash("💸 Not enough coins to send SMS.")
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
                response = requests.post("https://api.crownone.app/api/v1/Registration/verifysms", json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    database.update_user_coins(phone, user['coins'] - 1)
                    database.log_sms(phone, to, message)
                    flash("✅ Message sent successfully.")
                else:
                    flash("❌ Failed to send message.")
            except Exception as e:
                flash("⚠️ Network error.")

    updated_user = database.get_user(phone)
    return render_template("dashboard.html", coins=updated_user['coins'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
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
        action = request.form.get('action')
        phone = request.form.get('phone')
        if action == "add":
            coins = int(request.form.get('coins', 0))
            user = database.get_user(phone)
            if user:
                database.update_user_coins(phone, user['coins'] + coins)
                flash(f"✅ Added {coins} coins to {phone}")
            else:
                flash("❌ User not found.")
        elif action == "block":
            database.block_user(phone)
            flash(f"🚫 {phone} blocked.")
        elif action == "unblock":
            database.unblock_user(phone)
            flash(f"✅ {phone} unblocked.")

    users = database.get_all_users()
    logs = database.get_sms_logs()
    blocked = database.get_blocked_users()
    return render_template('admin_panel.html', users=users, logs=logs, blocked=blocked)

if __name__ == "__main__":
    app.run(debug=True)
