from flask import Flask, render_template, request, redirect, session
import csv
import os

app = Flask(__name__)
app.secret_key = "delsu_secret_key"

ADMIN_USERNAME = "successful"
ADMIN_PASSWORD = "empire223"   # case-insensitive handled below

FILE = "students.csv"

# create csv if not exists
if not os.path.exists(FILE):
    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["matric", "name", "level"])


# HOME
@app.route("/")
def home():
    return render_template("home.html")


# STUDENT LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form["matric"].strip().lower()

        with open(FILE, "r") as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                if row and row[0].strip().lower() == matric:
                    session["student"] = row[0]
                    return redirect("/dashboard")

        return "Invalid Matric Number"

    return render_template("login.html")


# STUDENT DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "student" not in session:
        return redirect("/login")

    return render_template("dashboard.html", matric=session["student"])


# ADMIN LOGIN
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        u = request.form["username"].strip().lower()
        p = request.form["password"].strip().lower()

        if u == ADMIN_USERNAME.lower() and p == ADMIN_PASSWORD.lower():
            session["admin"] = True
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")


# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    students = []

    with open(FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        students = list(reader)

    return render_template("admin.html", students=students)


# ADD STUDENT
@app.route("/add_student", methods=["POST"])
def add_student():
    if not session.get("admin"):
        return redirect("/admin")

    matric = request.form["matric"]
    name = request.form["name"]
    level = request.form["level"]

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([matric, name, level])

    return redirect("/admin/dashboard")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)