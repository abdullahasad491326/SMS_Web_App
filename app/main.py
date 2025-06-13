from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Dummy user and admin store
users = {}
admin = {
    "username": os.getenv("ADMIN_USERNAME", "PAKADMINLOGIN"),
    "password": os.getenv("ADMIN_PASSWORD", "24113576")
}
user_coins = {}
sms_logs = []
ip_blocked = {}

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        if phone in users:
            flash("User already exists.")
        else:
            users[phone] = password
            user_coins[phone] = 0
            flash("Registered successfully.")
            return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        if users.get(phone) == password:
            session["user"] = phone
            return redirect("/dashboard")
        else:
            flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == admin["username"] and
                request.form["password"] == admin["password"]):
            session["admin"] = True
            return redirect("/admin")
        else:
            flash("Invalid admin credentials.")
    return render_template("admin_login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = session.get("user")
    if not user:
        return redirect("/login")

    ip = request.remote_addr
    now = datetime.now()

    # IP block check
    if ip in ip_blocked and ip_blocked[ip] > now:
        return f"🚫 Your IP is temporarily blocked. Try again later."

    if request.method == "POST":
        number = request.form["number"]
        message = request.form["message"]
        if user_coins.get(user, 0) < 1:
            flash("Not enough coins.")
        else:
            # Simulate sending SMS
            user_coins[user] -= 1
            sms_logs.append({
                "user": user,
                "to": number,
                "msg": message,
                "time": now,
                "ip": ip
            })
            flash("✅ SMS sent.")

            # Abuse protection
            recent = [log for log in sms_logs if log["ip"] == ip and now - log["time"] < timedelta(hours=1)]
            if len(recent) >= 5:
                ip_blocked[ip] = now + timedelta(hours=2)

    coins = user_coins.get(user, 0)
    return render_template("dashboard.html", coins=coins)

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect("/admin/login")
    return render_template("admin.html", users=users, coins=user_coins, logs=sms_logs)

@app.route("/admin/add_coins", methods=["POST"])
def add_coins():
    if not session.get("admin"):
        return redirect("/admin/login")
    phone = request.form["phone"]
    amount = int(request.form["amount"])
    user_coins[phone] = user_coins.get(phone, 0) + amount
    flash(f"Added {amount} coins to {phone}")
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
