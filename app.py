from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "cse_portal_secret_2026"

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DATABASE ----------------
def db():
    return sqlite3.connect("portal.db")


# ---------------- INIT DB ----------------
def init_db():
    conn = db()
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
        filepath TEXT,
        category TEXT
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
        cur.execute("SELECT matric, name, level FROM students")
        students = cur.fetchall()
        conn.close()

        for s in students:
            if s[0].lower() == matric:
                session["student"] = s[0]
                session["name"] = s[1]
                session["level"] = s[2]
                return redirect("/dashboard")

        flash("Invalid matric number")

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
    conn.close()

    gallery, pdfs, past_questions, others = [], [], [], []

    for f in files:
        if f[3] == "gallery":
            gallery.append(f)
        elif f[3] == "pdf":
            pdfs.append(f)
        elif f[3] == "past_question":
            past_questions.append(f)
        else:
            others.append(f)

    return render_template(
        "downloads.html",
        gallery=gallery,
        pdfs=pdfs,
        past_questions=past_questions,
        others=others
    )


# ---------------- FILE DOWNLOAD ----------------
@app.route("/file/<filename>")
def file_download(filename):
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

    cur.execute("SELECT * FROM files")
    files = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        students=students,
        files=files,
        total=total
    )


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["POST"])
def add_student():
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students (matric, name, level) VALUES (?, ?, ?)",
        (request.form["matric"], request.form["name"], request.form["level"])
    )

    conn.commit()
    conn.close()

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
    conn.close()

    return redirect("/admin/dashboard")


# ---------------- UPLOAD FILE ----------------
@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("admin"):
        return redirect("/admin")

    if "file" not in request.files:
        flash("No file selected")
        return redirect("/admin/dashboard")

    files = request.files.getlist("file")
    category = request.form.get("category", "other")

    conn = db()
    cur = conn.cursor()

    for file in files:
        if file and file.filename:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            cur.execute(
                "INSERT INTO files (filename, filepath, category) VALUES (?, ?, ?)",
                (file.filename, file.filename, category)
            )

    conn.commit()
    conn.close()

    flash("Files uploaded successfully")
    return redirect("/admin/dashboard")


# ---------------- BULK UPLOAD ----------------
@app.route("/bulk_upload", methods=["POST"])
def bulk_upload():
    if not session.get("admin"):
        return redirect("/admin")

    file = request.files.get("file")

    if not file or file.filename == "":
        flash("No CSV file selected")
        return redirect("/admin/dashboard")

    stream = file.stream.read().decode("utf-8").splitlines()

    conn = db()
    cur = conn.cursor()

    inserted = 0

    for row in stream:
        if not row.strip():
            continue

        data = row.split(",")

        if len(data) == 3:
            cur.execute(
                "INSERT INTO students (matric, name, level) VALUES (?, ?, ?)",
                (data[0].strip(), data[1].strip(), data[2].strip())
            )
            inserted += 1

    conn.commit()
    conn.close()

    flash(f"{inserted} students uploaded successfully")
    return redirect("/admin/dashboard")


# ---------------- DELETE FILE ----------------
@app.route("/delete_file/<int:file_id>")
def delete_file(file_id):
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT filepath FROM files WHERE id = ?", (file_id,))
    row = cur.fetchone()

    if row:
        try:
            path = os.path.join(UPLOAD_FOLDER, row[0])
            if os.path.exists(path):
                os.remove(path)
        except:
            pass

    cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()

    return redirect("/admin/dashboard")


# ---------------- COURSES ----------------
@app.route("/courses")
def courses():
    if "student" not in session:
        return redirect("/login")

    matric = session.get("student", "").lower()
    is_cep = "cep" in matric

    return render_template("courses.html", is_cep=is_cep)


# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    query = request.args.get("query", "")

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    if not query:
        return render_template("search.html", results=[], query="")

    results = [
        s for s in students
        if query.lower() in s[1].lower() or query.lower() in s[2].lower()
    ]

    return render_template("search.html", results=results, query=query)


# ---------------- GPA ----------------
@app.route("/gpa", methods=["GET", "POST"])
def gpa():
    result = None

    if request.method == "POST":
        courses = int(request.form["courses"])

        points_map = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 0}

        total_points = 0
        total_units = 0

        for i in range(1, courses + 1):
            unit = int(request.form[f"unit{i}"])
            grade = request.form[f"grade{i}"]

            total_points += points_map.get(grade, 0) * unit
            total_units += unit

        if total_units:
            result = round(total_points / total_units, 2)

    return render_template("gpa.html", result=result)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)