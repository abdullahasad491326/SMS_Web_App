import sqlite3
from datetime import datetime

# --- CREATE TABLES IF NOT EXISTS ---
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

# --- REGISTER NEW USER ---
def register_user(phone, password):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
    conn.commit()
    conn.close()

# --- VALIDATE LOGIN ---
def validate_login(phone, password):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password))
    result = c.fetchone()
    conn.close()
    return result

# --- GET USER DETAILS ---
def get_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result

# --- DEDUCT COINS ---
def deduct_coin(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins - 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

# --- ADD COINS TO USER ---
def add_coins(phone, amount):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE phone = ?", (amount, phone))
    conn.commit()
    conn.close()

# --- LOG MESSAGE ---
def log_message(user, to_number, message):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (user, to_number, message, time) VALUES (?, ?, ?, ?)", 
              (user, to_number, message, timestamp))
    conn.commit()
    conn.close()

# --- GET ALL USERS (ADMIN PANEL) ---
def get_all_users():
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT phone, password, coins, blocked FROM users")
    users = c.fetchall()
    conn.close()
    return users

# --- GET ALL MESSAGES (ADMIN PANEL) ---
def get_all_messages():
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT user, to_number, message, time FROM messages ORDER BY id DESC")
    messages = c.fetchall()
    conn.close()
    return messages

# --- BLOCK USER ---
def block_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 1 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

# --- UNBLOCK USER ---
def unblock_user(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("UPDATE users SET blocked = 0 WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

# --- CHECK IF BLOCKED ---
def is_user_blocked(phone):
    conn = sqlite3.connect("sms.db")
    c = conn.cursor()
    c.execute("SELECT blocked FROM users WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()
    return result[0] == 1 if result else False
