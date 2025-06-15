from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)

users = {}
messages = []
admin_username = "PAKCYBER"
admin_password = "24113576"

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if phone in users:
            flash("User already registered.")
            return render_template('register.html')
        users[phone] = {"password": password, "coins": 10, "blocked": False}
        flash("Registered successfully!")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = users.get(phone)
        if user and user["password"] == password:
            if user["blocked"]:
                flash("User is blocked.")
                return render_template('login.html')
            session['user'] = phone
            return redirect('/dashboard')
        flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    phone = session['user']
    user = users[phone]
    if request.method == 'POST':
        mobile = request.form['mobile']
        message = request.form['message']
        if user["coins"] <= 0:
            flash("Not enough coins.")
            return render_template('dashboard.html', coins=user["coins"])
        payload = {
            "Code": 1234,
            "Mobile": mobile,
            "Message": message
        }
        headers = {
            "Host": "api.crownone.app",
            "accept": "application/json",
            "content-type": "application/json",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2"
        }
        response = requests.post("https://api.crownone.app/api/v1/Registration/verifysms",
                                 headers=headers,
                                 data=json.dumps(payload))
        user["coins"] -= 1
        messages.append({"user": phone, "to": mobile, "msg": message, "time": request.date})
        flash("SMS sent successfully!")
    return render_template('dashboard.html', coins=user["coins"])

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            session['admin'] = True
            return redirect('/admin_panel')
        flash("Invalid admin credentials.")
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin')
    if request.method == 'POST':
        action = request.form.get('action')
        number = request.form.get('number')
        if number in users:
            if action == "add_coins":
                users[number]['coins'] += 10
            elif action == "block":
                users[number]['blocked'] = True
            elif action == "unblock":
                users[number]['blocked'] = False
    return render_template('admin_panel.html', users=users, messages=messages)
