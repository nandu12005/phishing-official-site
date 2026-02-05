import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"   # allow http for localhost

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- GOOGLE LOGIN ----------------
google_bp = make_google_blueprint(
    client_id="  ",
    client_secret="  ",
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ],
    reprompt_consent=True
)
app.register_blueprint(google_bp, url_prefix="/login")

# ---------------- USER STORE ----------------
users = {}   # { email : hashed_password }

# ---------------- PASSWORD VALIDATION ----------------
def valid_password(password):
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{6,}$'
    return re.match(pattern, password)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", user=session["user"])

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not valid_password(password):
            flash("Password must contain letters, numbers & one special character")
            return redirect(url_for("register"))

        users[email] = generate_password_hash(password)
        flash("Registration successful")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # Google login
    if google.authorized:
        resp = google.get("/oauth2/v2/userinfo")
        email = resp.json()["email"]
        session["user"] = email
        return redirect(url_for("home"))

    # Normal login
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and check_password_hash(users[email], password):
            session["user"] = email
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")

    return render_template("login.html")

# ---------------- PHISHING CHECK ----------------
@app.route("/detect", methods=["POST"])
def detect():
    msg = request.form["message"]

    if "http" in msg.lower() or "link" in msg.lower() or "otp" in msg.lower():
        result = "⚠️ Phishing Message"
    else:
        result = "✅ Legitimate Message"

    return render_template("home.html", user=session["user"], result=result)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
