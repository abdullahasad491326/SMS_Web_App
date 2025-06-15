from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

limiter = Limiter(get_remote_address, app=app)

# Ensure DB exists
if not os.path.exists("users.db"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE users (phone TEXT PRIMARY KEY, password TEXT, coins INTEGER DEFAULT 10, blocked INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE messages (phone TEXT, target TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash("Passwords do not match")
            return render_template('register.html')
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        if c.fetchone():
            flash("User already registered")
            return render_template('register.html')
        c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
        conn.commit()
        conn.close()
        flash("Successfully registered! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = phone
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    phone = session['user']
    if request.method == 'POST':
        target = request.form['target']
        message = request.form['message']
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT coins, blocked FROM users WHERE phone = ?", (phone,))
        result = c.fetchone()
        if result and result[1] == 1:
            flash("You are blocked from sending messages.")
            return redirect(url_for('dashboard'))
        if result and result[0] > 0:
            payload = {
                "Code": "1234",
                "Mobile": target,
                "Message": message
            }
            headers = {
                "Host": "api.crownone.app",
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/4.9.2"
            }
            response = requests.post("https://api.crownone.app/api/v1/Registration/verifysms",
                                     json=payload, headers=headers)
            if response.status_code == 200:
                c.execute("INSERT INTO messages (phone, target, message) VALUES (?, ?, ?)", (phone, target, message))
                c.execute("UPDATE users SET coins = coins - 1 WHERE phone = ?", (phone,))
                conn.commit()
                flash("Message sent successfully!")
            else:
                flash("Failed to send message.")
        else:
            flash("Insufficient coins.")
        conn.close()
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Invalid admin credentials")
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    if request.method == 'POST':
        number = request.form['number']
        coins = int(request.form['coins'])
        c.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (coins, number))
        conn.commit()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    messages = c.fetchall()
    conn.close()
    return render_template('admin_panel.html', users=users, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)