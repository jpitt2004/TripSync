import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.secret_key = "tripsync-secret-key"

DATABASE = "database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# TIME FORMAT
# ============================================================

def format_time(time_value):

    if not time_value:
        return ""

    try:
        return datetime.strptime(
            time_value,
            "%H:%M"
        ).strftime(
            "%I:%M %p"
        ).lstrip("0")

    except ValueError:
        return time_value


# ============================================================
# DATABASE SETUP
# ============================================================

def init_db():

    connection = get_db_connection()

    # USERS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # TRIPS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trip_name TEXT NOT NULL,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            budget REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # TRIP MEMBERS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS trip_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES trips(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(trip_id, user_id)
        )
    """)

    # PENDING INVITATIONS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS pending_invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            invited_by INTEGER NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES trips(id),
            FOREIGN KEY(invited_by) REFERENCES users(id)
        )
    """)

    # ITINERARY
    connection.execute("""
        CREATE TABLE IF NOT EXISTS itinerary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            activity TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        )
    """)

    # EXPENSES
    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_by INTEGER NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES trips(id),
            FOREIGN KEY(paid_by) REFERENCES users(id)
        )
    """)

    # POLLS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        )
    """)

    # POLL OPTIONS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS poll_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            FOREIGN KEY(poll_id) REFERENCES polls(id)
        )
    """)

    # POLL VOTES
    connection.execute("""
        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(poll_id) REFERENCES polls(id),
            FOREIGN KEY(option_id) REFERENCES poll_options(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(poll_id, user_id)
        )
    """)

    # CHECKLIST
    connection.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            item TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# LOGIN CHECK
# ============================================================

def logged_in():
    return "user_id" in session


# ============================================================
# CHECK TRIP ACCESS
# ============================================================

def user_can_access_trip(connection, trip_id):

    result = connection.execute("""
        SELECT trips.id

        FROM trips

        LEFT JOIN trip_members
        ON trips.id = trip_members.trip_id

        WHERE trips.id = ?

        AND (
            trips.user_id = ?
            OR trip_members.user_id = ?
        )

        LIMIT 1
    """, (
        trip_id,
        session["user_id"],
        session["user_id"]
    )).fetchone()

    return result


# ============================================================
# GET USER'S TRIPS
# ============================================================

def get_accessible_trips(connection):

    return connection.execute("""
        SELECT DISTINCT trips.*

        FROM trips

        LEFT JOIN trip_members
        ON trips.id = trip_members.trip_id

        WHERE trips.user_id = ?
        OR trip_members.user_id = ?

        ORDER BY trips.start_date
    """, (
        session["user_id"],
        session["user_id"]
    )).fetchall()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    # IMPORTANT:
    # Home is PUBLIC.
    # It does NOT send logged-in users to login.

    return render_template("index.html")


# ============================================================
# SIGN UP
# ============================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please complete all fields.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        hashed_password = generate_password_hash(
            password
        )

        connection = get_db_connection()

        try:

            connection.execute("""
                INSERT INTO users
                (name, email, password)

                VALUES (?, ?, ?)
            """, (
                name,
                email,
                hashed_password
            ))

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            flash(
                "An account with that email already exists.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        connection.close()

        flash(
            "Account created successfully! Please log in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "signup.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            email,
        )).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(
        connection
    )

    connection.close()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        trips=trips
    )


# ============================================================
# CREATE TRIP
# ============================================================

@app.route(
    "/create-trip",
    methods=["GET", "POST"]
)
def create_trip():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        trip_name = request.form.get(
            "trip_name",
            ""
        ).strip()

        destination = request.form.get(
            "destination",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        )

        end_date = request.form.get(
            "end_date",
            ""
        )

        budget = request.form.get(
            "budget",
            "0"
        )

        if not trip_name or not destination:

            flash(
                "Please complete the trip information.",
                "error"
            )

            return render_template(
                "create-trip.html"
            )

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO trips
            (
                user_id,
                trip_name,
                destination,
                start_date,
                end_date,
                budget
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            trip_name,
            destination,
            start_date,
            end_date,
            budget
        ))

        connection.commit()

        connection.close()

        flash(
            "Trip created successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "create-trip.html"
    )


# ============================================================
# ADD FRIENDS
# ============================================================

@app.route(
    "/add-friends",
    methods=["GET", "POST"]
)
def add_friends():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(connection)

    if request.method == "POST":

        trip_id = request.form.get(
            "trip_id"
        )

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        trip = user_can_access_trip(
    connection,
    trip_id
)

        if not trip:

            connection.close()

            flash(
                "You can only add friends to trips you created.",
                "error"
            )

            return redirect(
                url_for("add_friends")
            )

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
        """, (
            email,
        )).fetchone()

        # FRIEND ALREADY HAS ACCOUNT
        if user:

            existing_member = connection.execute("""
                SELECT id
                FROM trip_members
                WHERE trip_id = ?
                AND user_id = ?
            """, (
                trip_id,
                user["id"]
            )).fetchone()

            # Don't add the trip owner again
            if user["id"] == session["user_id"]:

                flash(
                    "You are already the owner of this trip.",
                    "error"
                )

            elif existing_member:

                flash(
                    "That friend is already part of this trip.",
                    "error"
                )

            else:

                connection.execute("""
                    INSERT INTO trip_members
                    (
                        trip_id,
                        user_id
                    )

                    VALUES (?, ?)
                """, (
                    trip_id,
                    user["id"]
                ))

                connection.commit()

                flash(
                    f"{user['name']} was added to the trip!",
                    "success"
                )

        # FRIEND DOES NOT HAVE ACCOUNT
        else:

            existing_invitation = connection.execute("""
                SELECT id
                FROM pending_invitations
                WHERE trip_id = ?
                AND LOWER(email) = ?
            """, (
                trip_id,
                email
            )).fetchone()

            if existing_invitation:

                flash(
                    "An invitation is already pending for this email.",
                    "error"
                )

            else:

                connection.execute("""
                    INSERT INTO pending_invitations
                    (
                        trip_id,
                        email,
                        invited_by
                    )

                    VALUES (?, ?, ?)
                """, (
                    trip_id,
                    email,
                    session["user_id"]
                ))

                connection.commit()

                flash(
                    "Invitation created! They can create a TripSync account using this email.",
                    "success"
                )

        connection.close()

        return redirect(
            url_for("add_friends")
        )

    connection.close()

    return render_template(
        "add-friends.html",
        trips=trips
    )


# ============================================================
# ITINERARY
# ============================================================

@app.route(
    "/itinerary",
    methods=["GET", "POST"]
)
def itinerary():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(
        connection
    )

    if request.method == "POST":

        trip_id = request.form.get(
            "trip_id"
        )

        if not user_can_access_trip(
            connection,
            trip_id
        ):

            connection.close()

            flash(
                "You do not have access to this trip.",
                "error"
            )

            return redirect(
                url_for("itinerary")
            )

        connection.execute("""
            INSERT INTO itinerary
            (
                trip_id,
                activity,
                date,
                time,
                location
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            trip_id,

            request.form.get(
                "activity",
                ""
            ).strip(),

            request.form.get(
                "date",
                ""
            ),

            request.form.get(
                "time",
                ""
            ),

            request.form.get(
                "location",
                ""
            ).strip()
        ))

        connection.commit()

        connection.close()

        return redirect(
            url_for(
                "itinerary",
                trip_id=trip_id
            )
        )

    selected_trip_id = request.args.get(
        "trip_id",
        type=int
    )

    activities = []

    if (
        selected_trip_id
        and user_can_access_trip(
            connection,
            selected_trip_id
        )
    ):

        rows = connection.execute("""
            SELECT *
            FROM itinerary
            WHERE trip_id = ?
            ORDER BY date, time
        """, (
            selected_trip_id,
        )).fetchall()

        for row in rows:

            activity = dict(row)

            activity["display_time"] = format_time(
                row["time"]
            )

            activities.append(
                activity
            )

    connection.close()

    return render_template(
        "itinerary.html",
        trips=trips,
        selected_trip_id=selected_trip_id,
        activities=activities
    )


# ============================================================
# EXPENSES
# ============================================================

@app.route(
    "/expenses",
    methods=["GET", "POST"]
)
def expenses():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(
        connection
    )

    if request.method == "POST":

        trip_id = request.form.get(
            "trip_id"
        )

        if not user_can_access_trip(
            connection,
            trip_id
        ):

            connection.close()

            flash(
                "You do not have access to this trip.",
                "error"
            )

            return redirect(
                url_for("expenses")
            )

        description = request.form.get(
            "description",
            ""
        ).strip()

        amount = float(
            request.form.get(
                "amount",
                0
            )
        )

        connection.execute("""
            INSERT INTO expenses
            (
                trip_id,
                description,
                amount,
                paid_by
            )

            VALUES (?, ?, ?, ?)
        """, (
            trip_id,
            description,
            amount,
            session["user_id"]
        ))

        connection.commit()

        connection.close()

        return redirect(
            url_for(
                "expenses",
                trip_id=trip_id
            )
        )

    selected_trip_id = request.args.get(
        "trip_id",
        type=int
    )

    expense_rows = []

    total = 0

    if (
        selected_trip_id
        and user_can_access_trip(
            connection,
            selected_trip_id
        )
    ):

        expense_rows = connection.execute("""
            SELECT
                expenses.*,
                users.name AS payer

            FROM expenses

            JOIN users
            ON users.id = expenses.paid_by

            WHERE expenses.trip_id = ?

            ORDER BY expenses.id DESC
        """, (
            selected_trip_id,
        )).fetchall()

        total = sum(
            row["amount"]
            for row in expense_rows
        )

    connection.close()

    return render_template(
        "expenses.html",
        trips=trips,
        selected_trip_id=selected_trip_id,
        expenses=expense_rows,
        total=total
    )


# ============================================================
# VOTING
# ============================================================

@app.route(
    "/voting",
    methods=["GET", "POST"]
)
def voting():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(
        connection
    )

    if request.method == "POST":

        trip_id = request.form.get(
            "trip_id"
        )

        if not user_can_access_trip(
            connection,
            trip_id
        ):

            connection.close()

            flash(
                "You do not have access to this trip.",
                "error"
            )

            return redirect(
                url_for("voting")
            )

        question = request.form.get(
            "question",
            ""
        ).strip()

        options = [
            request.form.get(
                "option1",
                ""
            ).strip(),

            request.form.get(
                "option2",
                ""
            ).strip(),

            request.form.get(
                "option3",
                ""
            ).strip()
        ]

        options = [
            option
            for option in options
            if option
        ]

        if len(options) < 2:

            connection.close()

            flash(
                "Please enter at least two choices.",
                "error"
            )

            return redirect(
                url_for(
                    "voting",
                    trip_id=trip_id
                )
            )

        cursor = connection.execute("""
            INSERT INTO polls
            (
                trip_id,
                question
            )

            VALUES (?, ?)
        """, (
            trip_id,
            question
        ))

        poll_id = cursor.lastrowid

        for option in options:

            connection.execute("""
                INSERT INTO poll_options
                (
                    poll_id,
                    option_text
                )

                VALUES (?, ?)
            """, (
                poll_id,
                option
            ))

        connection.commit()

        connection.close()

        return redirect(
            url_for(
                "voting",
                trip_id=trip_id
            )
        )

    selected_trip_id = request.args.get(
        "trip_id",
        type=int
    )

    polls = []

    if (
        selected_trip_id
        and user_can_access_trip(
            connection,
            selected_trip_id
        )
    ):

        poll_rows = connection.execute("""
            SELECT *
            FROM polls
            WHERE trip_id = ?
            ORDER BY id DESC
        """, (
            selected_trip_id,
        )).fetchall()

        for poll in poll_rows:

            options = connection.execute("""
                SELECT
                    poll_options.*,
                    COUNT(poll_votes.id) AS votes

                FROM poll_options

                LEFT JOIN poll_votes
                ON poll_votes.option_id =
                   poll_options.id

                WHERE poll_options.poll_id = ?

                GROUP BY poll_options.id

                ORDER BY poll_options.id
            """, (
                poll["id"],
            )).fetchall()

            polls.append({
                "poll": poll,
                "options": options
            })

    connection.close()

    return render_template(
        "voting.html",
        trips=trips,
        selected_trip_id=selected_trip_id,
        polls=polls
    )


# ============================================================
# VOTE
# ============================================================

@app.route(
    "/vote/<int:poll_id>/<int:option_id>",
    methods=["POST"]
)
def vote(
    poll_id,
    option_id
):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    poll = connection.execute("""
        SELECT *
        FROM polls
        WHERE id = ?
    """, (
        poll_id,
    )).fetchone()

    if not poll:

        connection.close()

        flash(
            "Poll not found.",
            "error"
        )

        return redirect(
            url_for("voting")
        )

    if not user_can_access_trip(
        connection,
        poll["trip_id"]
    ):

        connection.close()

        flash(
            "You do not have access to this poll.",
            "error"
        )

        return redirect(
            url_for("voting")
        )

    try:

        connection.execute("""
            INSERT INTO poll_votes
            (
                poll_id,
                option_id,
                user_id
            )

            VALUES (?, ?, ?)
        """, (
            poll_id,
            option_id,
            session["user_id"]
        ))

        connection.commit()

        flash(
            "Your vote was recorded!",
            "success"
        )

    except sqlite3.IntegrityError:

        flash(
            "You already voted in this poll.",
            "error"
        )

    connection.close()

    return redirect(
        url_for(
            "voting",
            trip_id=poll["trip_id"]
        )
    )


# ============================================================
# CHECKLIST
# ============================================================

@app.route(
    "/checklist",
    methods=["GET", "POST"]
)
def checklist():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trips = get_accessible_trips(
        connection
    )

    if request.method == "POST":

        trip_id = request.form.get(
            "trip_id"
        )

        if not user_can_access_trip(
            connection,
            trip_id
        ):

            connection.close()

            flash(
                "You do not have access to this trip.",
                "error"
            )

            return redirect(
                url_for("checklist")
            )

        item = request.form.get(
            "item",
            ""
        ).strip()

        connection.execute("""
            INSERT INTO checklist
            (
                trip_id,
                item
            )

            VALUES (?, ?)
        """, (
            trip_id,
            item
        ))

        connection.commit()

        connection.close()

        return redirect(
            url_for(
                "checklist",
                trip_id=trip_id
            )
        )

    selected_trip_id = request.args.get(
        "trip_id",
        type=int
    )

    items = []

    if (
        selected_trip_id
        and user_can_access_trip(
            connection,
            selected_trip_id
        )
    ):

        items = connection.execute("""
            SELECT *
            FROM checklist
            WHERE trip_id = ?
            ORDER BY completed, id DESC
        """, (
            selected_trip_id,
        )).fetchall()

    connection.close()

    return render_template(
        "checklist.html",
        trips=trips,
        selected_trip_id=selected_trip_id,
        items=items
    )


# ============================================================
# TOGGLE CHECKLIST
# ============================================================

@app.route(
    "/checklist/<int:item_id>/toggle",
    methods=["POST"]
)
def toggle_checklist(item_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    item = connection.execute("""
        SELECT *
        FROM checklist
        WHERE id = ?
    """, (
        item_id,
    )).fetchone()

    if not item:

        connection.close()

        return redirect(
            url_for("checklist")
        )

    if not user_can_access_trip(
        connection,
        item["trip_id"]
    ):

        connection.close()

        flash(
            "You do not have access to this checklist.",
            "error"
        )

        return redirect(
            url_for("checklist")
        )

    connection.execute("""
        UPDATE checklist

        SET completed =
            CASE
                WHEN completed = 1
                THEN 0
                ELSE 1
            END

        WHERE id = ?
    """, (
        item_id,
    ))

    connection.commit()

    connection.close()

    return redirect(
        url_for(
            "checklist",
            trip_id=item["trip_id"]
        )
    )


# ============================================================
# TRIP DETAILS
# ============================================================

@app.route(
    "/trip/<int:trip_id>"
)
def trip_details(trip_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    trip = connection.execute("""
        SELECT *
        FROM trips
        WHERE id = ?
    """, (
        trip_id,
    )).fetchone()

    if not trip:

        connection.close()

        flash(
            "Trip not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    if not user_can_access_trip(
        connection,
        trip_id
    ):

        connection.close()

        flash(
            "You do not have access to this trip.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # Include the trip owner
    owner = connection.execute("""
        SELECT
            name,
            email

        FROM users

        WHERE id = ?
    """, (
        trip["user_id"],
    )).fetchone()

    members = connection.execute("""
        SELECT
            users.name,
            users.email

        FROM trip_members

        JOIN users
        ON users.id =
           trip_members.user_id

        WHERE trip_members.trip_id = ?
    """, (
        trip_id,
    )).fetchall()

    connection.close()

    all_members = []

    if owner:
        all_members.append(owner)

    all_members.extend(members)

    return render_template(
        "trip.html",
        trip=trip,
        members=all_members
    )


# ============================================================
# START DATABASE
# ============================================================

init_db()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )