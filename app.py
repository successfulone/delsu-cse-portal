# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import re

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Allowed matric numbers (sample)
ALLOWED_USERS = {
    "FOE/25/26/123456": {"name": "John Doe", "level": "100"},
    "FOE/25/26/654321": {"name": "Jane Smith", "level": "200"},
    "FOE/CEP/25/26/111222": {"name": "Peter Paul", "level": "100"},
}

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


def valid_matric(matric):
    pattern1 = r"^FOE/25/26/\d{6}$"
    pattern2 = r"^FOE/CEP/25/26/\d{6}$"
    return re.match(pattern1, matric) or re.match(pattern2, matric)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form.get("matric", "").strip().upper()

        if not valid_matric(matric):
            flash("Invalid matric number format.")
            return redirect(url_for("login"))

        if matric not in ALLOWED_USERS:
            flash("Matric number not recognized in CSE department.")
            return redirect(url_for("login"))

        session["user"] = matric
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = ALLOWED_USERS[session["user"]]
    return render_template(
        "dashboard.html",
        matric=session["user"],
        name=user["name"],
        level=user["level"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("admin_panel"))

        flash("Invalid admin login.")
        return redirect(url_for("admin"))

    return render_template("admin_login.html")


@app.route("/admin-panel")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("admin"))

    return render_template("admin.html", users=ALLOWED_USERS)


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)