from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

limiter = Limiter(get_remote_address, app=app)

ADMIN_USER = "PAKCYBER"
ADMIN_PASS = "24113576"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (phone TEXT PRIMARY KEY, password TEXT, coins INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (sender TEXT, receiver TEXT, message TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blocked (phone TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

# --- Helper Functions ---
def get_user(phone):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone=?", (phone,))
        return c.fetchone()

def update_user_coins(phone, coins):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET coins=? WHERE phone=?", (coins, phone))
        conn.commit()

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
            with sqlite3.connect('database.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (phone, password, coins) VALUES (?, ?, ?)", (phone, password, 0))
                conn.commit()
            flash("✅ Account created successfully!")
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = get_user(phone)
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
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT coins FROM users WHERE phone=?", (phone,))
        coins = c.fetchone()[0]
        c.execute("SELECT phone FROM blocked WHERE phone=?", (phone,))
        blocked = c.fetchone()

    if request.method == 'POST':
        if blocked:
            flash("🚫 You are blocked from sending SMS.")
        elif coins <= 0:
            flash("💸 Not enough coins to send SMS.")
        else:
            to = request.form['to']
            message = request.form['message']
            payload = {"Code": 1234, "Mobile": to, "Message": message}
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "user-agent": "okhttp/4.9.2"
            }
            try:
                res = requests.post("https://api.crownone.app/api/v1/Registration/verifysms", json=payload, headers=headers)
                if res.status_code == 200:
                    coins -= 1
                    update_user_coins(phone, coins)
                    with sqlite3.connect('database.db') as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO logs (sender, receiver, message, time) VALUES (?, ?, ?, ?)",
                                  (phone, to, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                    flash("✅ Message sent successfully.")
                else:
                    flash("❌ Failed to send SMS.")
            except Exception as e:
                flash("⚠️ Error: " + str(e))
        return redirect('/dashboard')

    return render_template('dashboard.html', coins=coins)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = ADMIN_USER
            return redirect('/admin_panel')
        else:
            flash("❌ Invalid admin credentials")
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin_login')
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        if request.method == 'POST':
            phone = request.form['phone']
            action = request.form['action']
            if action == 'add':
                coins = int(request.form['coins'])
                user = get_user(phone)
                if user:
                    new_balance = user[2] + coins
                    update_user_coins(phone, new_balance)
                    flash(f"✅ {coins} coins added to {phone}")
                else:
                    flash("❌ User not found")
            elif action == 'block':
                c.execute("INSERT OR IGNORE INTO blocked (phone) VALUES (?)", (phone,))
                conn.commit()
                flash(f"🚫 {phone} blocked")
            elif action == 'unblock':
                c.execute("DELETE FROM blocked WHERE phone=?", (phone,))
                conn.commit()
                flash(f"✅ {phone} unblocked")

        c.execute("SELECT phone, coins FROM users")
        users = c.fetchall()
        c.execute("SELECT * FROM logs ORDER BY time DESC LIMIT 20")
        logs = c.fetchall()
        c.execute("SELECT phone FROM blocked")
        blocked = [b[0] for b in c.fetchall()]

    return render_template('admin_panel.html', users=users, logs=logs, blocked=blocked)

if __name__ == '__main__':
    app.run(debug=True)
