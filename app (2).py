from flask import Flask, render_template, request, redirect, flash, session
import os
from cs50 import SQL


print("APP STARTED NEW VERSION")

app = Flask(__name__)
app.secret_key = "your_secret_key"

if not os.path.exists("tuition.db"):
    open("tuition.db", "w").close()

db = SQL("sqlite:///tuition.db")

db.execute("""CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, subject TEXT)""")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "khushi" and password == "321":
            session["user"] = username
            flash("Login Successfully 🎉")
            return redirect("/")

        flash(" Invalid Login 👎")
        return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged Out 👏")
    return redirect("/login")

@app.route("/")
def index():

    if not session.get("user"):
        return redirect("/login")

    subject = request.args.get("subject")
    q = request.args.get("q")
    msg = request.args.get("msg")

    if q:
        students = db.execute("SELECT * FROM students WHERE name LIKE ?", "%" + q + "%")

    elif subject:
        students = db.execute("SELECT * FROM students WHERE subject = ?", subject)

    else:
        students = db.execute("SELECT * FROM students")

    subjects = db.execute("SELECT DISTINCT subject FROM students")

    count = db.execute("SELECT COUNT(*) as total FROM students")[0]["total"]

    return render_template("index.html", students=students, subjects=subjects, msg=msg, count=count)

@app.route("/register", methods=["POST", "GET"])
def register():

    if not session.get("user"):
        return redirect("/login")

    if request.method == "POST":

        name = request.form.get("name")
        subject = request.form.get("subject")

        print("DEBUG:", request.method, name, subject)

        if not name or not subject:
            flash("⚠️ Missing Data")
            return redirect ("/register")

        existing = db.execute("SELECT * FROM students WHERE name=? AND subject=?", name, subject)

        if existing:
            flash("Student already registered")
            return redirect("/register")

        db.execute("INSERT INTO students (name, subject) VALUES (?, ?)", name, subject)

        flash("✅ Student Registered Successfully")

        return redirect ("/")

    return render_template("register.html")

@app.route("/delete/<int:id>", methods=["POST"])
def delete (id):

    if not session.get("user"):
        return redirect("/login")

    db.execute("DELETE FROM students WHERE id = ?", id)

    flash("🗑️ Student Deleted Successfully")

    return redirect("/")

@app.route("/search")
def search():

    if not session.get("user"):
        return redirect("/login")

    q = request.args.get("q")

    students = db.execute("SELECT * FROM students WHERE name LIKE ?", "%" + q + "%")

    return render_template("index.html", students=students)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if not session.get("user"):
        return redirect("/login")

    if request.method == "POST":

        name = request.form.get("name")
        subject = request.form.get("subject")

        if not name or not subject:
            flash("⚠️ Missing Data")
            return redirect (f"/edit/{id}")

        db.execute("UPDATE students SET name = ?, subject = ? WHERE id = ?", name, subject, id)

        flash("👍 Student Updated Successfully")
        return redirect("/")

    student = db.execute("SELECT * FROM students WHERE id = ?", id)

    return render_template("edit.html", student=student)

@app.route("/hello")
def hello():
    return "HELLO ROUTE WORKING"
