from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "delsu-secret-key"

DB_NAME = "students.db"

# -----------------------------
# CREATE DATABASE IF NOT EXISTS
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric TEXT UNIQUE,
            name TEXT,
            level TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    if "user" in session:
        return render_template("home.html", user=session["user"])
    return redirect("/login")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form["matric"].upper().strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE matric=?", (matric,))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = {
                "matric": user[1],
                "name": user[2],
                "level": user[3]
            }
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid Matric Number")

    return render_template("login.html")

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------------
# ADMIN (ADD STUDENTS)
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        matric = request.form["matric"].upper().strip()
        name = request.form["name"]
        level = request.form["level"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (matric, name, level) VALUES (?, ?, ?)",
                (matric, name, level)
            )
            conn.commit()
        except:
            pass

        conn.close()

    return render_template("admin.html")

# -----------------------------
# SEARCH
# -----------------------------
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"].upper()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE matric LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()

    conn.close()

    return render_template("search.html", results=results)

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)