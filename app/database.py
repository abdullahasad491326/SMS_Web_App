import sqlite3
from datetime import datetime

DB_NAME = "sms.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 0
        )
    ''')
    # Logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            receiver TEXT,
            message TEXT,
            time TEXT
        )
    ''')
    # Blocked users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked (
            phone TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def add_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password, coins) VALUES (?, ?, ?)", (phone, password, 0))
    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone, password, coins FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result

def decrement_coin(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins - 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def add_coins(phone, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (amount, phone))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone, coins FROM users")
    result = c.fetchall()
    conn.close()
    return result

def add_sms_log(user, receiver, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs (user, receiver, message, time) VALUES (?, ?, ?, ?)",
              (user, receiver, message, time))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user, receiver, message, time FROM logs ORDER BY time DESC")
    result = c.fetchall()
    conn.close()
    return result

def block_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO blocked (phone) VALUES (?)", (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM blocked WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def is_blocked(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone FROM blocked WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_all_blocked():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone FROM blocked")
    result = c.fetchall()
    conn.close()
    return [row[0] for row in result]
