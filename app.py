from flask import Flask, render_template, request ,redirect, url_for,flash,session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash
import sqlite3


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Basic route to test the Flask application
# @app.route("/")
# def home():
#     return "Hello A! Welcome to Flask 🚀" 

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

hashed = generate_password_hash("123456")

cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", 
               ("admins", hashed))

conn.commit()
conn.close()


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT ,
            email TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            conn.close()

            flash("Form submitted successfully!", "success")
            return redirect(url_for("home"))

        except sqlite3.IntegrityError:
            conn.close()

            flash("This email is already registered!", "error")
            return redirect(url_for("home"))

        # Handle form submission or other POST requests here
        pass
    return render_template("index.html")

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("login"))

    page = request.args.get("page", 1, type=int)
    per_page = 5

    offset = (page - 1) * per_page

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Get limited records
    cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset))
    contacts = cursor.fetchall()

    # Count total records
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    conn.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "admin.html",
        contacts=contacts,
        page=page,
        total_pages=total_pages
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            flash("Login successful!")
            return redirect(url_for("admin"))
        else:
            flash("Invalid credentials!")

    return render_template("login.html")


@app.route("/edit/<int:id>")
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    contact = cursor.fetchone()

    conn.close()

    return render_template("edit.html", contact=contact)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?, email = ?
        WHERE id = ?
    """, (name, email, id))

    conn.commit()
    conn.close()

    flash("Contact updated successfully!")

    return redirect(url_for("admin"))



@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Contact deleted successfully!")
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!")
    return redirect(url_for("login"))



@app.route("/about")
def about():
    return render_template("about.html")









if __name__ == "__main__":
    app.run(debug=False)
