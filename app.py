
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "cse_secret_key_25_26"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ---------------- STUDENT ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matric = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), default="CSE Student")
    level = db.Column(db.String(10), default="100L")

# ---------------- ANNOUNCEMENT ----------------
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- HOME ----------------
@app.route("/")
def home():
    announcements = Announcement.query.order_by(Announcement.date.desc()).all()
    return render_template("home.html", announcements=announcements)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        matric = request.form["matric"].strip()
        password = request.form["password"]

        student = Student.query.filter_by(matric=matric).first()

        if not student:
            return render_template("login.html", error="Matric not registered")

        if not check_password_hash(student.password, password):
            return render_template("login.html", error="Invalid password")

        session["user"] = matric
        return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    student = Student.query.filter_by(matric=session["user"]).first()
    return render_template("dashboard.html", student=student)

# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    if "user" not in session:
        return redirect(url_for("login"))

    query = request.args.get("q", "").lower()

    students = Student.query.filter(Student.matric.contains(query)).all()
    announcements = Announcement.query.filter(Announcement.title.contains(query)).all()
    files = [f for f in os.listdir(UPLOAD_FOLDER) if query in f.lower()]

    return render_template("search.html",
                           query=query,
                           students=students,
                           announcements=announcements,
                           files=files)

# ---------------- FILES ----------------
@app.route("/downloads")
def downloads():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("downloads.html", files=files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("login"))

    students = Student.query.all()
    announcements = Announcement.query.all()
    files = os.listdir(UPLOAD_FOLDER)

    return render_template("admin.html",
                           students=students,
                           announcements=announcements,
                           files=files)

# ---------------- FILE UPLOAD ----------------
@app.route("/admin/upload-file", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for("admin"))

# ---------------- ANNOUNCEMENT ----------------
@app.route("/admin/add-announcement", methods=["POST"])
def add_announcement():
    title = request.form["title"]
    content = request.form["content"]

    ann = Announcement(title=title, content=content)
    db.session.add(ann)
    db.session.commit()

    return redirect(url_for("admin"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)