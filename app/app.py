from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
import requests
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Rate limiting (by IP)
limiter = Limiter(key_func=get_remote_address, app=app)

DB = 'sms_app.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        phone TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        coins INTEGER DEFAULT 10,
                        blocked INTEGER DEFAULT 0
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sms_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone TEXT,
                        target TEXT,
                        message TEXT,
                        time TEXT
                    )''')
init_db()

# Admin credentials (you can change securely)
ADMIN_USERNAME = 'PAKCYBER'
ADMIN_PASSWORD = '24113576'

# Home route redirects
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone=?", (phone,))
            if c.fetchone():
                flash('User already exists')
                return redirect(url_for('register'))
            if password != confirm:
                flash('Passwords do not match')
                return redirect(url_for('register'))
            c.execute("INSERT INTO users (phone, password, coins) VALUES (?, ?, 10)", (phone, password))
            conn.commit()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone=? AND password=?", (phone, password))
            user = c.fetchone()
            if user:
                if user[3] == 1:
                    flash("User is blocked")
                    return redirect(url_for('login'))
                session['phone'] = phone
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials")
    return render_template('login.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def dashboard():
    if 'phone' not in session:
        return redirect(url_for('login'))

    message_status = ''
    if request.method == 'POST':
        target = request.form['target']
        message = request.form['message']
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE phone=?", (session['phone'],))
            coins = c.fetchone()[0]
            if coins < 1:
                message_status = "Not enough coins"
            else:
                api = "https://api.crownone.app/api/v1/Registration/verifysms"
                payload = {
                    "Code": 1234,
                    "Mobile": target,
                    "Message": message
                }
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "okhttp/4.9.2"
                }
                try:
                    response = requests.post(api, json=payload, headers=headers, timeout=10)
                    if response.status_code == 200:
                        c.execute("UPDATE users SET coins = coins - 1 WHERE phone=?", (session['phone'],))
                        c.execute("INSERT INTO sms_logs (phone, target, message, time) VALUES (?, ?, ?, ?)",
                                  (session['phone'], target, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        message_status = "SMS sent successfully"
                    else:
                        message_status = "API Error: Failed to send"
                except Exception:
                    message_status = "Network Error"
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT coins FROM users WHERE phone=?", (session['phone'],))
        coins = c.fetchone()[0]
    return render_template('dashboard.html', coins=coins, message_status=message_status)

# Admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Invalid admin credentials")
    return render_template('admin_login.html')

# Admin panel
@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = [{'phone': row[0], 'password': row[1], 'coins': row[2], 'blocked': row[3]} for row in c.fetchall()]
        c.execute("SELECT * FROM sms_logs ORDER BY id DESC LIMIT 100")
        sms_logs = [{'phone': row[1], 'target': row[2], 'message': row[3], 'time': row[4]} for row in c.fetchall()]
    return render_template('admin_panel.html', users=users, sms_logs=sms_logs)

# Add coins
@app.route('/admin_add_coins', methods=['POST'])
def admin_add_coins():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    phone = request.form['phone']
    coins = int(request.form['coins'])
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET coins = coins + ? WHERE phone=?", (coins, phone))
        conn.commit()
    return redirect(url_for('admin_panel'))

# Block/Unblock
@app.route('/admin_block/<phone>')
def admin_block(phone):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET blocked=1 WHERE phone=?", (phone,))
        conn.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin_unblock/<phone>')
def admin_unblock(phone):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET blocked=0 WHERE phone=?", (phone,))
        conn.commit()
    return redirect(url_for('admin_panel'))

# Logout routes
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
