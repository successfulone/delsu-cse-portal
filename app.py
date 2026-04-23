from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "cse_portal_secret_2026"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DATABASE ----------------
def db():
    conn = sqlite3.connect("portal.db")
    return conn


# AUTO CREATE TABLES (FIX FOR RENDER ERROR)
def init_db():
    conn = sqlite3.connect("portal.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matric TEXT,
        name TEXT,
        level TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT
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
        matric = request.form["matric"].strip().lower()

        conn = db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()

        for s in students:
            if s[1].lower() == matric:
                session["student"] = s[1]
                session["name"] = s[2]
                session["level"] = s[3]
                return redirect("/dashboard")

        flash("Invalid matric number. Please contact admin.")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "student" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        matric=session["student"],
        name=session["name"],
        level=session["level"]
    )


# ---------------- DOWNLOADS ----------------
@app.route("/downloads")
def downloads():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files")
    files = cur.fetchall()
    return render_template("downloads.html", files=files)


# ---------------- FILE DOWNLOAD ----------------
@app.route("/file/<filename>")
def file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        u = request.form["username"].lower()
        p = request.form["password"].lower()

        if u == "successful" and p == "empire223":
            session["admin"] = True
            return redirect("/admin/dashboard")

        flash("Invalid admin login details")

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    return render_template("admin.html", students=students, total=total)


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["POST"])
def add_student():
    if not session.get("admin"):
        return redirect("/admin")

    matric = request.form["matric"]
    name = request.form["name"]
    level = request.form["level"]

    conn = db()
    cur = conn.cursor()

    cur.execute("INSERT INTO students (matric, name, level) VALUES (?, ?, ?)",
                (matric, name, level))
    conn.commit()

    return redirect("/admin/dashboard")


# ---------------- DELETE STUDENT ----------------
@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()

    return redirect("/admin/dashboard")


# ---------------- COURSES (FULL FEATURE ADDED CLEANLY) ----------------
@app.route("/courses")
def courses():
    if "student" not in session:
        return redirect("/login")

    matric = session.get("student", "").lower()

    # AUTO DETECT CEP OR REGULAR (OPTION A)
    is_cep = "cep" in matric or "ce/" in matric

    regular_courses = [
        "CSC101 - Introduction to Computer Science",
        "CSC102 - Programming Fundamentals",
        "CSC103 - Computer Systems",
        "CSC104 - Problem Solving Techniques",
        "GST101 - Communication Skills"
    ]

    cep_courses = [
        "CEP101 - Foundations of Education",
        "CEP102 - Teaching Methods",
        "CSC105 - Computer Education Basics",
        "CSC106 - ICT in Education",
        "GST102 - Use of English"
    ]

    return render_template(
        "courses.html",
        is_cep=is_cep,
        regular=regular_courses,
        cep=cep_courses
    )


# ---------------- SEARCH ----------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    results = []

    for s in students:
        if query.lower() in s[1].lower() or query.lower() in s[2].lower():
            results.append(s)

    return render_template("search.html", results=results, query=query)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)