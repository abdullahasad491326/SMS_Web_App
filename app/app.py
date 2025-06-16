from flask import Flask, render_template, request, redirect, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import requests
import database as db

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
        if db.user_exists(phone):
            flash("❌ User already exists.", "error")
        else:
            db.add_user(phone, password)
            flash("✅ Account created successfully!", "success")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if db.verify_user(phone, password):
            session['user'] = phone
            flash("✅ Login successful.", "success")
            return redirect('/dashboard')
        else:
            flash("❌ Invalid credentials.", "error")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    phone = session['user']
    user_data = db.get_user(phone)
    if request.method == 'POST':
        if db.is_blocked(phone):
            flash("🚫 You are blocked from sending SMS.", "error")
        elif user_data['coins'] <= 0:
            flash("💸 Not enough coins to send SMS.", "error")
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
                    db.update_coins(phone, -1)
                    db.log_sms(phone, to, message)
                    flash("✅ Message sent successfully.", "success")
                else:
                    flash("❌ Failed to send SMS.", "error")
            except Exception as e:
                flash(f"⚠️ API Error: {str(e)}", "error")
        return redirect('/dashboard')  # Prevent resend on refresh
    return render_template('dashboard.html', coins=user_data['coins'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect('/login')

@app.route('/admin_', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = username
            return redirect('/admin_panel')
        else:
            flash("❌ Invalid admin credentials", "error")
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin_')
    if request.method == 'POST':
        action = request.form.get('action')
        phone = request.form.get('phone')
        if action == 'add':
            try:
                coins = int(request.form.get('coins'))
                if db.user_exists(phone):
                    db.update_coins(phone, coins)
                    flash(f"✅ {coins} coins added to {phone}", "success")
                else:
                    flash("❌ User not found.", "error")
            except:
                flash("⚠️ Invalid coin amount.", "error")
        elif action == 'block':
            db.block_user(phone)
            flash(f"🚫 User {phone} blocked.", "error")
        elif action == 'unblock':
            db.unblock_user(phone)
            flash(f"✅ User {phone} unblocked.", "success")
    users = db.get_all_users()
    logs = db.get_sms_logs()
    blocked = db.get_blocked_users()
    return render_template('admin_panel.html', users=users, logs=logs, blocked=blocked)

if __name__ == '__main__':
    app.run(debug=True)
