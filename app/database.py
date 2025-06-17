import psycopg2
from datetime import datetime
import os

DB_URL = os.getenv("postgresql://sms_db_5ifm_user:A2oJ2caHlym0fLu8j2RgQBzyEZk3nVGH@dpg-d18p6fili9vc73fr1mg0-a/sms_db_5ifm")

def get_conn():
    return psycopg2.connect(DB_URL, sslmode='require')

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 10,
            blocked BOOLEAN DEFAULT FALSE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_phone TEXT,
            to_number TEXT,
            message TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def add_user(phone, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (phone, password))
    conn.commit()
    cur.close()
    conn.close()

def get_user(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def validate_user(phone, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_user_coins(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE phone = %s", (phone,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else 0

def update_user_coins(phone, coins):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = %s WHERE phone = %s", (coins, phone))
    conn.commit()
    cur.close()
    conn.close()

def block_user(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET blocked = TRUE WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()
    conn.close()

def unblock_user(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET blocked = FALSE WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()
    conn.close()

def is_blocked(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT blocked FROM users WHERE phone = %s", (phone,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else False

def log_sms(user, to, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (user_phone, to_number, message) VALUES (%s, %s, %s)", (user, to, message))
    conn.commit()
    cur.close()
    conn.close()

def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY phone")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def get_sms_logs():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_phone, to_number, message, time FROM messages ORDER BY time DESC")
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs
