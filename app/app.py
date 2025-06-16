from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import requests

app = Flask(__name__)
app.secret_key = 'supersecret'

# ADMIN LOGIN
ADMIN_USER = 'PAKCYBER'
ADMIN_PASS = '030411'

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE phone=?", (phone,))
        if cur.fetchone():
            return "User already exists!"
        cur.execute("INSERT INTO users (phone, password, coins, blocked) VALUES (?, ?, ?, ?)", (phone, password, 25, 0))
        con.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE phone=? AND password=?", (phone, password))
        user = cur.fetchone()
        if user:
            if user['blocked']:
                return "User blocked"
            session['user'] = user['phone']
            return redirect('/dashboard')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/admin_', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin_panel')
        return "Wrong admin credentials"
    return render_template('admin_login.html')

@app.route('/admin_panel')
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin_')
    con = get_db()
    users = con.execute("SELECT * FROM users").fetchall()
    logs = con.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    return render_template('admin_panel.html', users=users, logs=logs)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    phone = session['user']
    con = get_db()
    cur = con.cursor()
    user = cur.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()

    if request.method == 'POST':
        to = request.form['to']
        message = request.form['message']
        if user['coins'] <= 0:
            return "Not enough coins"
        payload = {
            "Code": "123456",
            "Mobile": to,
            "Message": message
        }
        requests.post("https://api.crownone.app/api/v1/Registration/verifysms", json=payload)
        new_coins = user['coins'] - 1
        cur.execute("UPDATE users SET coins=? WHERE phone=?", (new_coins, phone))
        cur.execute("INSERT INTO messages (sender, receiver, message, time) VALUES (?, ?, ?, ?)", (phone, to, message, datetime.datetime.now()))
        con.commit()
        return redirect('/dashboard')

    return render_template('dashboard.html', coins=user['coins'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin_action', methods=['POST'])
def admin_action():
    if 'admin' not in session:
        return redirect('/admin_')
    phone = request.form['phone']
    con = get_db()
    cur = con.cursor()
    if 'add' in request.form:
        coins = int(request.form['coins'])
        cur.execute("UPDATE users SET coins = coins + ? WHERE phone=?", (coins, phone))
    elif 'block' in request.form:
        cur.execute("UPDATE users SET blocked = 1 WHERE phone=?", (phone,))
    elif 'unblock' in request.form:
        cur.execute("UPDATE users SET blocked = 0 WHERE phone=?", (phone,))
    con.commit()
    return redirect('/admin_panel')
