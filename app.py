import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]

DATABASE_URL = os.getenv("DATABASE_URL")

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )
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
    """Verify the Neon schema exists; tables are managed in Neon SQL Editor."""
    connection = get_db_connection()
    try:
        tables = connection.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """).fetchall()
        existing = {row["table_name"] for row in tables}
        required = {
            "users", "trips", "trip_members", "pending_invitations",
            "itinerary", "expenses", "polls", "poll_options",
            "poll_votes", "checklist"
        }
        missing = required - existing
        if missing:
            raise RuntimeError(f"Missing Neon tables: {', '.join(sorted(missing))}")
    finally:
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

        WHERE trips.id = %s

        AND (
            trips.user_id = %s
            OR trip_members.user_id = %s
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

        WHERE trips.user_id = %s
        OR trip_members.user_id = %s

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
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)
        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
            """, (name, email, hashed_password))

            # Find the account that was just created
            new_user = connection.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            ).fetchone()

            # Find invitations sent to this email
            invitations = connection.execute("""
                SELECT trip_id
                FROM pending_invitations
                WHERE LOWER(email) = %s
            """, (email,)).fetchall()

            # Add the new user to each invited trip
            for invitation in invitations:
                connection.execute("""
                    INSERT INTO trip_members (trip_id, user_id)
                    VALUES (%s, %s)
                    ON CONFLICT (trip_id, user_id) DO NOTHING
                """, (invitation["trip_id"], new_user["id"]))

            # Remove invitations that have been accepted
            connection.execute("""
                DELETE FROM pending_invitations
                WHERE LOWER(email) = %s
            """, (email,))

            connection.commit()

        except psycopg.errors.UniqueViolation:
            connection.rollback()
            connection.close()
            flash(
                "An account with that email already exists.",
                "error"
            )
            return render_template("signup.html")

        connection.close()
        flash(
            "Account created successfully! Please log in.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("signup.html")

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
            WHERE email = %s
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

            VALUES (%s, %s, %s, %s, %s, %s)
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
            WHERE LOWER(email) = %s
        """, (
            email,
        )).fetchone()

        # FRIEND ALREADY HAS ACCOUNT
        if user:

            existing_member = connection.execute("""
                SELECT id
                FROM trip_members
                WHERE trip_id = %s
                AND user_id = %s
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

                    VALUES (%s, %s)
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
                WHERE trip_id = %s
                AND LOWER(email) = %s
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

                    VALUES (%s, %s, %s)
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

            VALUES (%s, %s, %s, %s, %s)
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
            WHERE trip_id = %s
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

            VALUES (%s, %s, %s, %s)
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

            WHERE expenses.trip_id = %s

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

            VALUES (%s, %s)
            RETURNING id
        """, (
            trip_id,
            question
        ))

        poll_id = cursor.fetchone()["id"]

        for option in options:

            connection.execute("""
                INSERT INTO poll_options
                (
                    poll_id,
                    option_text
                )

                VALUES (%s, %s)
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
            WHERE trip_id = %s
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

                WHERE poll_options.poll_id = %s

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
        WHERE id = %s
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

            VALUES (%s, %s, %s)
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

    except psycopg.errors.UniqueViolation:

        connection.rollback()
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

            VALUES (%s, %s)
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
            WHERE trip_id = %s
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
        WHERE id = %s
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

        WHERE id = %s
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
        WHERE id = %s
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

        WHERE id = %s
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

        WHERE trip_members.trip_id = %s
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
# DELETE TRIP
# ============================================================

@app.route(
    "/delete-trip/<int:trip_id>",
    methods=["POST"]
)
def delete_trip(trip_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    # Make sure the logged-in user owns this trip
    trip = connection.execute("""
        SELECT *
        FROM trips
        WHERE id = %s
        AND user_id = %s
    """, (
        trip_id,
        session["user_id"]
    )).fetchone()

    if not trip:

        connection.close()

        flash(
            "You can only delete trips that you created.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # Delete checklist items
    connection.execute("""
        DELETE FROM checklist
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Delete expenses
    connection.execute("""
        DELETE FROM expenses
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Delete itinerary activities
    connection.execute("""
        DELETE FROM itinerary
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Delete poll votes
    connection.execute("""
        DELETE FROM poll_votes
        WHERE poll_id IN (
            SELECT id
            FROM polls
            WHERE trip_id = %s
        )
    """, (
        trip_id,
    ))

    # Delete poll options
    connection.execute("""
        DELETE FROM poll_options
        WHERE poll_id IN (
            SELECT id
            FROM polls
            WHERE trip_id = %s
        )
    """, (
        trip_id,
    ))

    # Delete polls
    connection.execute("""
        DELETE FROM polls
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Delete pending invitations
    connection.execute("""
        DELETE FROM pending_invitations
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Delete trip members
    connection.execute("""
        DELETE FROM trip_members
        WHERE trip_id = %s
    """, (
        trip_id,
    ))

    # Finally delete the trip itself
    connection.execute("""
        DELETE FROM trips
        WHERE id = %s
        AND user_id = %s
    """, (
        trip_id,
        session["user_id"]
    ))

    connection.commit()
    connection.close()

    flash(
        "Trip deleted successfully.",
        "success"
    )

    return redirect(
        url_for("dashboard")
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