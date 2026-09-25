from flask import Flask, render_template, request
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)


# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# -------------------------
# CREATE DATABASE TABLES
# -------------------------

def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trip_name TEXT NOT NULL,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            budget REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS trip_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    connection.commit()
    connection.close()


# -------------------------
# HOME PAGE
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# SIGNUP
# -------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check passwords
        if password != confirm_password:
            return "Passwords do not match."

        # Hash password before saving
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return """
            <h2>Account already exists</h2>
            <p>An account with this email already exists.</p>
            <a href="/signup">Try another email</a>
            """

        connection.close()

        return """
        <h2>Account created successfully!</h2>
        <p>Welcome to TripSync.</p>
        <a href="/">Go Home</a>
        """

    return render_template("signup.html")


# -------------------------
# CREATE TRIP
# -------------------------

@app.route("/create-trip", methods=["GET", "POST"])
def create_trip():

    if request.method == "POST":

        trip_name = request.form["trip_name"]
        destination = request.form["destination"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        budget = request.form["budget"]

        print(
            trip_name,
            destination,
            start_date,
            end_date,
            budget
        )

        message = f"{trip_name} was created successfully!"

        return render_template(
            "create-trip.html",
            message=message
        )

    return render_template("create-trip.html")


# -------------------------
# START APPLICATION
# -------------------------

init_db()


if __name__ == "__main__":
    app.run(debug=True)