import sqlite3

def connect():
    return sqlite3.connect("data.db", check_same_thread=False)

def init_db():
    db = connect()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (phone TEXT PRIMARY KEY, password TEXT, coins INTEGER DEFAULT 0, blocked INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, to_number TEXT, message TEXT, time TEXT)")
    db.commit()

def get_user(phone):
    db = connect()
    return db.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()

def add_user(phone, password):
    db = connect()
    db.execute("INSERT INTO users (phone, password, coins, blocked) VALUES (?, ?, ?, ?)", (phone, password, 0, 0))
    db.commit()

def validate_user(phone, password):
    db = connect()
    return db.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password)).fetchone()

def get_user_coins(phone):
    db = connect()
    row = db.execute("SELECT coins FROM users WHERE phone = ?", (phone,)).fetchone()
    return row[0] if row else 0

def update_user_coins(phone, coins):
    db = connect()
    db.execute("UPDATE users SET coins = ? WHERE phone = ?", (coins, phone))
    db.commit()

def block_user(phone):
    db = connect()
    db.execute("UPDATE users SET blocked = 1 WHERE phone = ?", (phone,))
    db.commit()

def unblock_user(phone):
    db = connect()
    db.execute("UPDATE users SET blocked = 0 WHERE phone = ?", (phone,))
    db.commit()

def is_blocked(phone):
    db = connect()
    row = db.execute("SELECT blocked FROM users WHERE phone = ?", (phone,)).fetchone()
    return row[0] == 1 if row else False

def log_sms(user, to, message):
    db = connect()
    db.execute("INSERT INTO logs (user, to_number, message, time) VALUES (?, ?, ?, datetime('now'))", (user, to, message))
    db.commit()

def get_all_users():
    db = connect()
    return db.execute("SELECT * FROM users").fetchall()

def get_sms_logs():
    db = connect()
    return db.execute("SELECT * FROM logs ORDER BY time DESC").fetchall()
