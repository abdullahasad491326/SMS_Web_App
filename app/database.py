import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://sms_db_5ifm_user:A2oJ2caHlym0fLu8j2RgQBzyEZk3nVGH@dpg-d18p6fili9vc73fr1mg0-a/sms_db_5ifm"

def connect():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    db = connect()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT,
            coins INTEGER DEFAULT 0,
            blocked BOOLEAN DEFAULT FALSE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user TEXT,
            to_number TEXT,
            message TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

def get_user(phone):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
    result = cur.fetchone()
    db.close()
    return result

def add_user(phone, password):
    db = connect()
    cur = db.cursor()
    cur.execute("INSERT INTO users (phone, password, coins, blocked) VALUES (%s, %s, %s, %s)", (phone, password, 0, False))
    db.commit()
    db.close()

def validate_user(phone, password):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, password))
    result = cur.fetchone()
    db.close()
    return result

def get_user_coins(phone):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT coins FROM users WHERE phone = %s", (phone,))
    row = cur.fetchone()
    db.close()
    return row["coins"] if row else 0

def update_user_coins(phone, coins):
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE users SET coins = %s WHERE phone = %s", (coins, phone))
    db.commit()
    db.close()

def block_user(phone):
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE users SET blocked = TRUE WHERE phone = %s", (phone,))
    db.commit()
    db.close()

def unblock_user(phone):
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE users SET blocked = FALSE WHERE phone = %s", (phone,))
    db.commit()
    db.close()

def is_blocked(phone):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT blocked FROM users WHERE phone = %s", (phone,))
    row = cur.fetchone()
    db.close()
    return row["blocked"] if row else False

def log_sms(user, to, message):
    db = connect()
    cur = db.cursor()
    cur.execute("INSERT INTO logs (user, to_number, message) VALUES (%s, %s, %s)", (user, to, message))
    db.commit()
    db.close()

def get_all_users():
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    result = cur.fetchall()
    db.close()
    return result

def get_sms_logs():
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT * FROM logs ORDER BY time DESC")
    result = cur.fetchall()
    db.close()
    return result
