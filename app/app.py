from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup (ensure database.db exists with correct schema)
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        if existing:
            conn.close()
            return 'User already exists!'
        conn.execute('INSERT INTO users (phone, password, coins, blocked) VALUES (?, ?, 10, 0)', (phone, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE phone = ? AND password = ?', (phone, password)).fetchone()
        conn.close()
        if user:
            if user['blocked']:
                return 'User is blocked.'
            session['phone'] = phone
            return redirect(url_for('dashboard'))
        return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'phone' not in session:
        return redirect(url_for('login'))

    phone = session['phone']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()

    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()

        if user['coins'] <= 0:
            conn.close()
            return render_template('dashboard.html', phone=phone, coins=user['coins'], error='Not enough coins')

        conn.execute('INSERT INTO messages (user_phone, recipient, message, timestamp) VALUES (?, ?, ?, ?)',
                     (phone, recipient, message, now))
        conn.execute('UPDATE users SET coins = coins - 1 WHERE phone = ?', (phone,))
        conn.commit()
        conn.close()
        return render_template('dashboard.html', phone=phone, coins=user['coins'] - 1, success='Message sent successfully.')

    return render_template('dashboard.html', phone=phone, coins=user['coins'])

@app.route('/admin_', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'PAKCYBER' and password == 'YOUR_ADMIN_PASSWORD':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        return 'Invalid admin credentials'
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()

    if request.method == 'POST':
        phone = request.form['phone']
        coins = request.form.get('coins')

        if 'add' in request.form:
            conn.execute('UPDATE users SET coins = coins + ? WHERE phone = ?', (coins, phone))
        elif 'block' in request.form:
            conn.execute('UPDATE users SET blocked = 1 WHERE phone = ?', (phone,))
        elif 'unblock' in request.form:
            conn.execute('UPDATE users SET blocked = 0 WHERE phone = ?', (phone,))

        conn.commit()

    users = conn.execute('SELECT * FROM users').fetchall()
    messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('admin_panel.html', users=users, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
    
