# database.py

users = {}
sms_logs = []
blocked_users = []

def get_users():
    return users

def get_logs():
    return sms_logs

def get_blocked_users():
    return blocked_users

def add_user(phone, password):
    users[phone] = {'password': password, 'coins': 0}

def user_exists(phone):
    return phone in users

def check_password(phone, password):
    return users[phone]['password'] == password

def get_user_data(phone):
    return users.get(phone)

def deduct_coin(phone):
    if users[phone]['coins'] > 0:
        users[phone]['coins'] -= 1

def add_log(user, to, message, time):
    sms_logs.append({'user': user, 'to': to, 'message': message, 'time': time})

def add_coins(phone, coins):
    users[phone]['coins'] += coins

def is_blocked(phone):
    return phone in blocked_users

def block_user(phone):
    if phone not in blocked_users:
        blocked_users.append(phone)

def unblock_user(phone):
    if phone in blocked_users:
        blocked_users.remove(phone)
