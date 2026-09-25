from flask import Flask, render_template, request, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "tripsync-secret-key"


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

    connection.execute("""
        CREATE TABLE IF NOT EXISTS pending_invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            invited_by INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips (id),
            FOREIGN KEY (invited_by) REFERENCES users (id)
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
# SIGN UP
# -------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match."

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
        <a href="/login">Sign In</a>
        """

    return render_template("signup.html")


# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect("/dashboard")

        return """
        <h2>Invalid email or password</h2>
        <p>Please check your information and try again.</p>
        <a href="/login">Try Again</a>
        """

    return render_template("login.html")


# -------------------------
# DASHBOARD
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return """
        <h2>Please sign in first.</h2>
        <a href="/login">Sign In</a>
        """

    connection = get_db_connection()

    trips = connection.execute(
        """
        SELECT *
        FROM trips
        WHERE user_id = ?
        ORDER BY start_date
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        trips=trips
    )


# -------------------------
# CREATE TRIP
# -------------------------

@app.route("/create-trip", methods=["GET", "POST"])
def create_trip():

    if "user_id" not in session:
        return """
        <h2>Please sign in first.</h2>
        <a href="/login">Sign In</a>
        """

    if request.method == "POST":

        trip_name = request.form["trip_name"]
        destination = request.form["destination"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        budget = request.form["budget"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO trips
            (user_id, trip_name, destination, start_date, end_date, budget)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                trip_name,
                destination,
                start_date,
                end_date,
                budget
            )
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template("create-trip.html")


# -------------------------
# ADD FRIENDS
# -------------------------

@app.route("/add-friends", methods=["GET", "POST"])
def add_friends():

    if "user_id" not in session:
        return """
        <h2>Please sign in first.</h2>
        <a href="/login">Sign In</a>
        """

    connection = get_db_connection()

    if request.method == "POST":

        trip_id = request.form["trip_id"]
        email = request.form["email"].strip().lower()

        # Make sure the selected trip belongs to the
        # person currently signed in.
        trip = connection.execute(
            """
            SELECT *
            FROM trips
            WHERE id = ? AND user_id = ?
            """,
            (trip_id, session["user_id"])
        ).fetchone()

        if not trip:
            connection.close()

            return """
            <h2>Trip not found</h2>
            <p>You can only add people to trips you created.</p>
            <a href="/add-friends">Try Again</a>
            """

        # Check whether the person already has an account.
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,)
        ).fetchone()

        if user:

            # Check whether they are already a member.
            existing_member = connection.execute(
                """
                SELECT *
                FROM trip_members
                WHERE trip_id = ? AND user_id = ?
                """,
                (trip_id, user["id"])
            ).fetchone()

            if existing_member:

                connection.close()

                return render_template(
                    "add-friends.html",
                    trips=get_user_trips(),
                    message="That person is already part of this trip."
                )

            # Add existing user to trip.
            connection.execute(
                """
                INSERT INTO trip_members (trip_id, user_id)
                VALUES (?, ?)
                """,
                (trip_id, user["id"])
            )

            connection.commit()
            connection.close()

            return render_template(
                "add-friends.html",
                trips=get_user_trips(),
                message=f"{user['name']} was added to the trip! 🎉"
            )

        else:

            # Check whether an invitation already exists.
            existing_invitation = connection.execute(
                """
                SELECT *
                FROM pending_invitations
                WHERE trip_id = ? AND LOWER(email) = ?
                """,
                (trip_id, email)
            ).fetchone()

            if existing_invitation:

                connection.close()

                return render_template(
                    "add-friends.html",
                    trips=get_user_trips(),
                    message="An invitation has already been created for that email."
                )

            # Create pending invitation.
            connection.execute(
                """
                INSERT INTO pending_invitations
                (trip_id, email, invited_by)
                VALUES (?, ?, ?)
                """,
                (trip_id, email, session["user_id"])
            )

            connection.commit()
            connection.close()

            return render_template(
                "add-friends.html",
                trips=get_user_trips(),
                message=f"An invitation was created for {email}! 💌"
            )

    trips = get_user_trips(connection)

    connection.close()

    return render_template(
        "add-friends.html",
        trips=trips,
        message=None
    )


# -------------------------
# GET USER'S TRIPS
# -------------------------

def get_user_trips(connection=None):

    close_connection = False

    if connection is None:
        connection = get_db_connection()
        close_connection = True

    trips = connection.execute(
        """
        SELECT *
        FROM trips
        WHERE user_id = ?
        ORDER BY start_date
        """,
        (session["user_id"],)
    ).fetchall()

    if close_connection:
        connection.close()

    return trips


# -------------------------
# START APPLICATION
# -------------------------

init_db()


if __name__ == "__main__":
    app.run(debug=True)