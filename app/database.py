import sqlite3
from datetime import datetime

DB_NAME = 'data.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    phone TEXT PRIMARY KEY,
                    password TEXT,
                    coins INTEGER DEFAULT 0,
                    is_blocked INTEGER DEFAULT 0
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS sms_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    recipient TEXT,
                    message TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

def add_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password, coins, is_blocked) VALUES (?, ?, ?, ?)",
              (phone, password, 0, 0))
    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone, password, coins, is_blocked FROM users WHERE phone=?", (phone,))
    result = c.fetchone()
    conn.close()
    return result

def validate_user(phone, password):
    user = get_user(phone)
    return user and user[1] == password

def update_coins(phone, coins):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (coins, phone))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone, coins, is_blocked FROM users")
    users = c.fetchall()
    conn.close()
    return users

def block_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_blocked = 1 WHERE phone=?", (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_blocked = 0 WHERE phone=?", (phone,))
    conn.commit()
    conn.close()

def is_user_blocked(phone):
    user = get_user(phone)
    return user[3] == 1 if user else False

def deduct_coin(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins - 1 WHERE phone=?", (phone,))
    conn.commit()
    conn.close()

def log_sms(sender, recipient, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sms_logs (sender, recipient, message, timestamp) VALUES (?, ?, ?, ?)",
              (sender, recipient, message, timestamp))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT sender, recipient, message, timestamp FROM sms_logs ORDER BY timestamp DESC")
    logs = c.fetchall()
    conn.close()
    return logs
