import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 phone TEXT PRIMARY KEY,
                 password TEXT NOT NULL,
                 coins INTEGER DEFAULT 10,
                 blocked INTEGER DEFAULT 0
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user TEXT,
                 to_number TEXT,
                 message TEXT,
                 time TEXT
                 )''')

    conn.commit()
    conn.close()

def register_user(phone, password):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
    conn.commit()
    conn.close()

def validate_login(phone, password):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password))
    result = c.fetchone()
    conn.close()
    return result

def get_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result

def deduct_coin(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins - 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def log_message(user, to, message):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (user, to_number, message, time) VALUES (?, ?, ?, ?)", (user, to, message, time))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_messages():
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    messages = c.fetchall()
    conn.close()
    return messages

def add_coins(phone, amount):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (amount, phone))
    conn.commit()
    conn.close()

def block_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 0 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()
    
