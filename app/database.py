import sqlite3

DB_NAME = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_phone TEXT,
            target_number TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT phone, password, coins, blocked FROM users WHERE phone = ?', (phone,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(phone, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (phone, password, coins) VALUES (?, ?, 0)', (phone, password))
    conn.commit()
    conn.close()

def update_coins(phone, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET coins = coins + ? WHERE phone = ?', (amount, phone))
    conn.commit()
    conn.close()

def block_user(phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET blocked = 1 WHERE phone = ?', (phone,))
    conn.commit()
    conn.close()

def unblock_user(phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET blocked = 0 WHERE phone = ?', (phone,))
    conn.commit()
    conn.close()

def is_blocked(phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT blocked FROM users WHERE phone = ?', (phone,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT phone, coins, blocked FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def add_sms_log(user_phone, target_number, message, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sms_logs (user_phone, target_number, message, timestamp) VALUES (?, ?, ?, ?)',
                   (user_phone, target_number, message, timestamp))
    conn.commit()
    conn.close()

def get_sms_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_phone, target_number, message, timestamp FROM sms_logs ORDER BY id DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs
