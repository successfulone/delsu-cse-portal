from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = "cse_portal_secret_2026"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


# ---------------- DB CONNECTION ----------------
def db():
    conn = sqlite3.connect("portal.db")
    return conn


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


# ---------------- DOWNLOAD FILES ----------------
@app.route("/downloads")
def downloads():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files")
    files = cur.fetchall()
    return render_template("downloads.html", files=files)


# ---------------- DOWNLOAD ACTION ----------------
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


# ---------------- FILE UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("admin"):
        return redirect("/admin")

    file = request.files["file"]

    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        conn = db()
        cur = conn.cursor()

        cur.execute("INSERT INTO files (filename, filepath) VALUES (?, ?)",
                    (file.filename, path))
        conn.commit()

    return redirect("/admin/dashboard")


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