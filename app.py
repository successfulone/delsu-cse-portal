from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret-key-change-this"

DB = "database.db"
UPLOAD_FOLDER = "uploads"

ADMIN_USERNAME = "successful"
ADMIN_PASSWORD = "Empire223@"


# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        matric TEXT PRIMARY KEY,
        name TEXT,
        level TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form["matric"].upper()

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT * FROM students WHERE matric=?", (matric,))
        user = cur.fetchone()

        conn.close()

        if user:
            session["student"] = matric
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid Matric Number")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "student" not in session:
        return redirect("/login")

    return render_template("dashboard.html", matric=session["student"])


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
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

    files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []

    return render_template("admin.html", students=students, files=files)


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["POST"])
def add_student():
    matric = request.form["matric"].upper()
    name = request.form["name"]
    level = request.form["level"]

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO students VALUES (?,?,?)",
                (matric, name, level))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- DELETE STUDENT ----------------
@app.route("/delete_student/<matric>")
def delete_student(matric):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE matric=?", (matric,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- SEARCH STUDENT ----------------
@app.route("/search_student", methods=["POST"])
def search_student():
    matric = request.form["matric"].upper()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE matric=?", (matric,))
    student = cur.fetchone()

    conn.close()

    return render_template("admin.html", search=student)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin_login")


if __name__ == "__main__":
    app.run(debug=True)