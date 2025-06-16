from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Admin credentials
ADMIN_USERNAME = 'PAKCYBER'
ADMIN_PASSWORD = 'admin123'

def get_db_connection():
    conn = sqlite3.connect('sms.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def get_all_messages():
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
    conn.close()
    return messages

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute("INSERT INTO users (phone, password, coins, blocked) VALUES (?, ?, 10, 0)", (phone, password))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password)).fetchone()
        conn.close()

        if user:
            session['user'] = phone
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin_')
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        to = request.form['to']
        msg = request.form['message']
        user = session['user']
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        user_data = conn.execute("SELECT coins, blocked FROM users WHERE phone = ?", (user,)).fetchone()

        if user_data and user_data['blocked'] == 0 and user_data['coins'] > 0:
            conn.execute("INSERT INTO messages (user, to_number, message, time) VALUES (?, ?, ?, ?)", (user, to, msg, time))
            conn.execute("UPDATE users SET coins = coins - 1 WHERE phone = ?", (user,))
            conn.commit()
            conn.close()
            return render_template('dashboard.html', message='Message sent successfully.', coins=user_data['coins'] - 1)
        else:
            conn.close()
            return render_template('dashboard.html', message='Blocked or insufficient coins.', coins=user_data['coins'])

    conn = get_db_connection()
    user_data = conn.execute("SELECT coins FROM users WHERE phone = ?", (session['user'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', coins=user_data['coins'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin_')
def admin_panel():
    if 'admin_logged_in' not in session:
        return redirect('/admin_login')
    
    try:
        users = get_all_users()
        messages = get_all_messages()
        return render_template('admin_dashboard.html', users=users, messages=messages)
    except Exception as e:
        return f"Admin Panel Load Error: {str(e)}"

@app.route('/add_coins', methods=['POST'])
def add_coins():
    if 'admin_logged_in' in session:
        phone = request.form['phone']
        coins = int(request.form['coins'])
        conn = get_db_connection()
        conn.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (coins, phone))
        conn.commit()
        conn.close()
    return redirect('/admin_')

@app.route('/block_user', methods=['POST'])
def block_user():
    if 'admin_logged_in' in session:
        phone = request.form['phone']
        conn = get_db_connection()
        conn.execute("UPDATE users SET blocked = 1 WHERE phone = ?", (phone,))
        conn.commit()
        conn.close()
    return redirect('/admin_')

@app.route('/unblock_user', methods=['POST'])
def unblock_user():
    if 'admin_logged_in' in session:
        phone = request.form['phone']
        conn = get_db_connection()
        conn.execute("UPDATE users SET blocked = 0 WHERE phone = ?", (phone,))
        conn.commit()
        conn.close()
    return redirect('/admin_')

if __name__ == '__main__':
    app.run(debug=True)
