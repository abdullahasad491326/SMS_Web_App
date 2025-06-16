import sqlite3
from datetime import datetime

DB_NAME = "sms_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    ''')
    # Create SMS logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password, coins) VALUES (?, ?, ?)", (phone, password, 0))
    conn.commit()
    conn.close()

def validate_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_user_coins(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_coins(phone, coins):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = ? WHERE phone = ?", (coins, phone))
    conn.commit()
    conn.close()

def block_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 0 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def is_blocked(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT blocked FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def log_sms(sender, receiver, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sms_logs (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)",
              (sender, receiver, message, timestamp))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone, coins, blocked FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_sms_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT sender, receiver, message, timestamp FROM sms_logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()
    return logs
