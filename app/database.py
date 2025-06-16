import sqlite3
from datetime import datetime

DB_NAME = "data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            recipient TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked_users (
            phone TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'phone': row[0], 'password': row[1], 'coins': row[2]}
    return None

def create_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password, coins) VALUES (?, ?, ?)", (phone, password, 0))
    conn.commit()
    conn.close()

def update_user_coins(phone, coins):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = ? WHERE phone = ?", (coins, phone))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return [{'phone': row[0], 'password': row[1], 'coins': row[2]} for row in rows]

def log_sms(user, recipient, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO sms_logs (user, recipient, message, timestamp) VALUES (?, ?, ?, ?)",
              (user, recipient, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_sms_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM sms_logs ORDER BY timestamp DESC")
    logs = c.fetchall()
    conn.close()
    return [{'user': row[1], 'to': row[2], 'message': row[3], 'time': datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")} for row in logs]

def block_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO blocked_users (phone) VALUES (?)", (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM blocked_users WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def is_blocked(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM blocked_users WHERE phone = ?", (phone,))
    blocked = c.fetchone()
    conn.close()
    return blocked is not None

def get_blocked_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT phone FROM blocked_users")
    blocked = c.fetchall()
    conn.close()
    return [row[0] for row in blocked]
