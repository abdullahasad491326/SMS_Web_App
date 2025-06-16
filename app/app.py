from flask import Flask, render_template, request, redirect, session, url_for
import database
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Create tables at startup
database.create_tables()

# Home page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = database.get_user(phone)
        if user:
            return "User already exists."
        database.register_user(phone, password)
        return redirect('/login')
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = database.validate_login(phone, password)
        if user and user[3] == 0:  # Not blocked
            session['user'] = phone
            return redirect('/dashboard')
        elif user and user[3] == 1:
            return "You are blocked."
        return "Invalid login."
    return render_template('login.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    user = database.get_user(session['user'])

    message_status = None
    if request.method == 'POST':
        to_number = request.form['to_number']
        message = request.form['message']

        if user[2] <= 0:
            message_status = "Insufficient coins!"
        else:
            # Send SMS
            response = requests.post("https://api.crownone.app/api/v1/Registration/verifysms", json={
                "Code": "1234",
                "Mobile": to_number,
                "Message": message
            })

            if response.status_code == 200:
                database.log_message(session['user'], to_number, message)
                database.deduct_coin(session['user'])
                message_status = "Message sent successfully."
            else:
                message_status = "Failed to send message."

        # Reload updated coin balance
        user = database.get_user(session['user'])

    return render_template('dashboard.html', coins=user[2], message_status=message_status)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Admin login
@app.route('/admin_', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'PAKCYBER' and password == '24113576':
            session['admin'] = True
            return redirect('/admin_panel')
        return "Invalid admin credentials"
    return render_template('admin_login.html')

# Admin Panel
@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin_')

    message = None

    if request.method == 'POST':
        phone = request.form['phone']
        coins = request.form.get('coins')
        action = request.form['action']

        if action == 'add':
            database.add_coins(phone, int(coins))
            message = f"Added {coins} coins to {phone}"
        elif action == 'block':
            database.block_user(phone)
            message = f"{phone} blocked"
        elif action == 'unblock':
            database.unblock_user(phone)
            message = f"{phone} unblocked"

    users = database.get_all_users()
    messages = database.get_all_messages()
    return render_template('admin_panel.html', users=users, logs=messages, message=message)

# Run app
if __name__ == '__main__':
    app.run(debug=True)
