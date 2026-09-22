from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/create-trip", methods=["GET", "POST"])
def create_trip():
    message = None

    if request.method == "POST":
        trip_name = request.form["trip_name"]
        destination = request.form["destination"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        budget = request.form["budget"]

        print(trip_name, destination, start_date, end_date, budget)

        message = f"{trip_name} was created successfully!"

    return render_template("create-trip.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)