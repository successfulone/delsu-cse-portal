from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os
import csv

app = Flask(__name__)
app.secret_key = "secret"

DB = "database.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DB ----------------
def init():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        matric TEXT PRIMARY KEY,
        name TEXT,
        level TEXT
    )
    """)

    conn.commit()
    conn.close()

init()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        matric = request.form["matric"].strip().upper()

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT * FROM students WHERE UPPER(matric)=?", (matric,))
        user = cur.fetchone()

        conn.close()

        if user:
            session["student"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "student" not in session:
        return redirect("/login")

    return render_template("dashboard.html", matric=session["student"])


# ---------------- ADMIN LOGIN (CASE INSENSITIVE) ----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]

        if username == "successful" and password == "Empire223@":
            session["admin"] = True
            return redirect("/admin")

    return render_template("admin_login.html")


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin_login")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    files = os.listdir(UPLOAD_FOLDER)

    return render_template("admin.html", students=students, files=files)


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["POST"])
def add_student():
    matric = request.form["matric"].strip().upper()
    name = request.form["name"]
    level = request.form["level"]

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO students VALUES (?,?,?)",
                (matric, name, level))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- BULK CSV UPLOAD ----------------
@app.route("/upload_students", methods=["POST"])
def upload_students():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                cur.execute("INSERT OR REPLACE INTO students VALUES (?,?,?)",
                            (row[0].upper(), row[1], row[2] if len(row)>2 else "ND"))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- FILE UPLOAD (FIXED 404) ----------------
@app.route("/upload_file", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect("/admin")


# ---------------- DOWNLOAD FILES ----------------
@app.route("/downloads/<filename>")
def downloads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------- DELETE ----------------
@app.route("/delete/<matric>")
def delete(matric):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE matric=?", (matric,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)