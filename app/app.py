from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'database.db'
ADMIN_USERNAME = 'PAKCYBER'
ADMIN_PASSWORD = '24113576'  # Change this
SMS_API_URL = 'https://api.crownone.app/api/v1/Registration/verifysms'

# ---------- DATABASE ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        phone TEXT PRIMARY KEY,
                        password TEXT,
                        coins INTEGER DEFAULT 0,
                        blocked INTEGER DEFAULT 0
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
                        user TEXT,
                        to_number TEXT,
                        message TEXT,
                        timestamp TEXT
                    )''')
        conn.commit()

init_db()

# ---------- ROUTES ----------
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE phone=?', (phone,))
            if c.fetchone():
                return 'Phone number already registered.'
            c.execute('INSERT INTO users (phone, password, coins) VALUES (?, ?, 25)', (phone, password))
            conn.commit()
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE phone=? AND password=? AND blocked=0', (phone, password))
            if c.fetchone():
                session['user'] = phone
                return redirect('/dashboard')
        return 'Invalid credentials or account blocked.'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    message_sent = False
    if request.method == 'POST':
        recipient = request.form['to']
        message = request.form['message']
        user = session['user']

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT coins FROM users WHERE phone=?', (user,))
            coins = c.fetchone()[0]

            if coins <= 0:
                return 'Insufficient coins.'

            payload = {
                "Code": "1234",
                "Mobile": recipient,
                "Message": message
            }
            try:
                requests.post(SMS_API_URL, json=payload)
                c.execute('UPDATE users SET coins = coins - 1 WHERE phone=?', (user,))
                c.execute('INSERT INTO messages (user, to_number, message, timestamp) VALUES (?, ?, ?, ?)',
                          (user, recipient, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                message_sent = True
            except:
                return 'Failed to send message.'

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT coins FROM users WHERE phone=?', (session['user'],))
        coins = c.fetchone()[0]

    return render_template('dashboard.html', coins=coins, message_sent=message_sent)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/admin_', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = username
            return redirect('/admin_dashboard')
        return 'Invalid admin credentials.'
    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin_')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        users = c.execute('SELECT * FROM users').fetchall()
        messages = c.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()

    if request.method == 'POST':
        phone = request.form['phone']
        coins = request.form.get('coins')
        if 'add' in request.form:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('UPDATE users SET coins = coins + ? WHERE phone=?', (coins, phone))
                conn.commit()
        elif 'block' in request.form:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('UPDATE users SET blocked = 1 WHERE phone=?', (phone,))
                conn.commit()
        elif 'unblock' in request.form:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('UPDATE users SET blocked = 0 WHERE phone=?', (phone,))
                conn.commit()
        return redirect('/admin_dashboard')

    return render_template('admin_dashboard.html', users=users, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
    
