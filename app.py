from flask import Flask, render_template, request, redirect, session
import csv
import os

app = Flask(__name__)
app.secret_key = "secretkey"

ADMIN_USERNAME = "successful"
ADMIN_PASSWORD = "Empire223@"

STUDENTS_FILE = "students.csv"

# Ensure file exists
if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["matric", "name", "level"])

@app.route("/")
def home():
    return render_template("login.html")

# STUDENT LOGIN (matric only)
@app.route("/login", methods=["POST"])
def login():
    matric = request.form["matric"]

    with open(STUDENTS_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row and row[0].lower() == matric.lower():
                session["student"] = row[0]
                return redirect("/dashboard")

    return "Invalid Matric Number"

@app.route("/dashboard")
def dashboard():
    if "student" not in session:
        return redirect("/")

    return render_template("dashboard.html", matric=session["student"])

# ADMIN LOGIN PAGE
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        u = request.form["username"].lower()
        p = request.form["password"]

        if u == ADMIN_USERNAME.lower() and p == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    students = []

    with open(STUDENTS_FILE, "r") as f:
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

    with open(STUDENTS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([matric, name, level])

    return redirect("/admin/dashboard")

if __name__ == "__main__":
    app.run(debug=True)