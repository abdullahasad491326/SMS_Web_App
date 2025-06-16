from flask import Flask, render_template, request, redirect, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import requests
from database import (
    init_db, get_user, add_user, validate_user,
    get_user_coins, update_user_coins, log_sms,
    block_user, unblock_user, is_blocked,
    get_all_users, get_sms_logs
)

init_db()

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
        if get_user(phone):
            flash("❌ User already exists.")
        else:
            add_user(phone, password)
            flash("✅ Account created!")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if validate_user(phone, password):
            session['user'] = phone
            flash("✅ Login successful.")
            return redirect('/dashboard')
        else:
            flash("❌ Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("50/minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    phone = session['user']
    if is_blocked(phone):
        flash("🚫 You are blocked from sending SMS.")
        return render_template('dashboard.html', coins=0)

    coins = get_user_coins(phone)
    if request.method == 'POST':
        to = request.form['to']
        message = request.form['message']
        if coins <= 0:
            flash("💸 Not enough coins.")
        else:
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
                    update_user_coins(phone, coins - 1)
                    log_sms(phone, to, message)
                    flash("✅ Message sent successfully.")
                else:
                    flash("❌ Failed to send.")
            except:
                flash("⚠️ Network error while sending.")
    return render_template('dashboard.html', coins=get_user_coins(phone))

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
            current = get_user_coins(phone)
            update_user_coins(phone, current + coins)
            flash(f"✅ Added {coins} coins to {phone}")
        elif action == "block":
            block_user(phone)
            flash(f"🚫 {phone} blocked.")
        elif action == "unblock":
            unblock_user(phone)
            flash(f"✅ {phone} unblocked.")
    
    users = get_all_users()
    logs = get_sms_logs()
    return render_template('admin_panel.html', users=users, logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
