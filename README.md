
# TripSync

TripSync is a collaborative group travel planning web application that helps users organize trips, manage itineraries, track expenses, make group decisions, and keep track of trip tasks in one place.

## Live Application

**TripSync:** https://tripsync-gw90.onrender.com

**GitHub Repository:** https://github.com/jpitt2004/TripSync

## Project Overview

TripSync was developed as a team software engineering project using Flask and SQLite. The application provides a centralized place for users and groups to plan and manage trips.

Instead of relying on multiple group chats, notes, and applications, users can organize important trip information through one website.

## Features

### 1. Creating and Organizing a Trip

**Persona:** Maya — Trip Organizer

**Scenario:** Maya is planning a trip to Miami with four friends. The group is using different group chats to discuss the trip, making it difficult to keep track of the destination, dates, and plans. Maya needs one place to organize the trip and invite her friends. She creates a trip in TripSync, enters the trip name, destination, travel dates, and budget, and invites friends who already have TripSync accounts.

**User Story:** As a trip organizer, I want to create a trip with its destination and travel dates so that I can organize the trip information in one place.

**Feature:** Create & Join Trips — Users can create trips and add friends who already have TripSync accounts.

---

### 2. Planning the Group Itinerary

**Persona:** Jordan — Group Member

**Scenario:** Jordan and the group have several activities planned for their Miami trip. Their plans are being discussed through messages, making it easy to forget when or where activities are happening. Jordan needs a shared place where everyone can view the schedule. Jordan adds a dinner reservation to the TripSync itinerary with the restaurant, date, time, and location.

**User Story:** As a group member, I want to add activities to the shared itinerary so that everyone can see the group's plans.

**Feature:** Shared Trip Itinerary — Group members can add and view trip activities.

---

### 3. Tracking Shared Expenses

**Persona:** Alexis — Budget-Conscious Traveler

**Scenario:** Alexis pays $200 for an activity during the group trip. She wants everyone to know how much was spent and who paid for it. Alexis enters the expense description and amount in TripSync. The expense tracker records the payment so the group can view its spending.

**User Story:** As a group member, I want to record a shared expense so that the group can keep track of its spending.

**Feature:** Trip Expense Tracker — Users can record expenses, view amounts, and see who paid.

---

### 4. Deciding on a Group Activity

**Persona:** Jordan — Group Member

**Scenario:** The group cannot decide whether to visit a museum or go on a boat tour. Everyone has a different preference, and discussing the options through group messages is becoming confusing. Jordan creates a vote in TripSync with the two activity options. Each group member submits a choice, and the group can view the results to help make the decision.

**User Story:** As a group member, I want to create a vote with different activity options so that the group can make decisions together.

**Feature:** Group Voting — Members can create polls, vote, and view results.

---

### 5. Preparing for the Trip

**Persona:** Maya — Trip Organizer

**Scenario:** As the trip gets closer, Maya realizes that the group needs to complete tasks such as packing, buying tickets, and confirming reservations. She is worried that some tasks may be forgotten. Maya creates checklist items in TripSync. Members mark items as completed so everyone can see what has been handled.

**User Story:** As a group member, I want to create checklist items so that important trip tasks are not forgotten.

**Feature:** Trip Checklist — Members can add tasks and mark them as completed.

---

### 6. Deleting a Trip

**Persona:** Maya — Trip Organizer

**Scenario:** Maya decides that a planned trip is no longer needed. Since she created the trip, she wants to remove it from TripSync along with the information associated with the trip. Maya selects the delete option and confirms the deletion. The trip and its related information are removed from the application for the group.

**User Story:** As a trip organizer, I want to delete a trip I created so that I can remove trips that are no longer needed.

**Feature:** Delete Trip — Only the trip owner can delete a trip.

---

## User Authentication

TripSync provides user authentication so users can:

- Create an account
- Log in
- Log out
- Access their trips through the dashboard
- Add registered friends to shared trips

**Important:** Friends must already have a TripSync account before they can be added to an existing trip. Sending invitations to people without accounts is not currently supported.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Git
- GitHub
- Docker
- Render

## Project Structure

```text
TripSync/
│
├── app.py
├── README.md
├── TESTING.md
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── create-trip.html
│   ├── add-friends.html
│   ├── itinerary.html
│   ├── expenses.html
│   ├── voting.html
│   ├── checklist.html
│   └── trip.html
│
└── tests/
    ├── README.md
    ├── test_auth.py
    ├── test_trip_features.py
    └── test_trip_planning.py
```

**Note:** TripSync creates and uses a local SQLite database (`database.db`). This file is excluded from Git tracking to prevent local account and trip data from being uploaded to GitHub.

## Running TripSync Locally

### Requirements

- Python 3
- Git

### Installation

**Step 1: Clone the repository.**

```bash
git clone https://github.com/jpitt2004/TripSync.git
```

**Step 2: Open the project folder.**

```bash
cd TripSync
```

**Step 3: Install the required dependencies.**

```bash
pip install -r requirements.txt
```

**Step 4: Start the Flask application.**

```bash
python app.py
```

**Step 5: Open the application in your browser.**

http://127.0.0.1:5000

Once the application opens, create an account, log in, and begin planning a trip.

## Running TripSync with Docker

TripSync can also run inside a Docker container.

Make sure Docker Desktop is installed and running.

**Step 1: Build the Docker image.**

```bash
docker build -t tripsync .
```

**Step 2: Run the Docker container.**

```bash
docker run --rm -p 5000:5000 tripsync
```

**Step 3: Open the application.**

http://localhost:5000

The application will run inside the Docker container.

Press `Ctrl + C` in the terminal to stop the container.

## Testing

TripSync was tested using automated route tests and manual feature testing.

### Automated Testing

Run the automated tests using:

```bash
python -m unittest discover -s tests
```

**Results:** 10 automated tests passed during local verification.

The automated tests check application routes and expected HTTP responses.

### Manual Testing

The following functionality was manually tested:

- User registration and login
- Incorrect login credentials
- Creating trips
- Adding registered friends
- Viewing trip information
- Adding itinerary activities
- Recording expenses
- Creating and participating in votes
- Creating and completing checklist items
- Deleting trips as the owner
- Navigating between application pages

Additional testing information is available in `TESTING.md`.

## Deployment

TripSync was containerized using Docker and deployed to Render.

**Live Application:** https://tripsync-gw90.onrender.com

Users can visit the website, register an account, log in, and test the available features.

### Storage Limitation

TripSync currently uses SQLite for database storage.

The deployed application uses Render's temporary filesystem, meaning saved accounts and trip information may be lost when the service restarts or redeploys.

For demonstrations and instructor review, users can create accounts and trips directly through the live website.

A future improvement would be to migrate the application to persistent PostgreSQL storage.

## Team Members

- Jeniya Pittman
- JaDaeyah Murray
- Brandon Howell

## Future Improvements

Possible improvements include:

- Persistent PostgreSQL database storage
- Invitations for users who do not already have accounts
- Email notifications for trip invitations
- Automatic expense splitting between participants
- Improved mobile responsiveness
- Additional trip customization options

## Conclusion

TripSync demonstrates how software engineering concepts can be applied to develop a collaborative travel planning application. Through Flask, SQLite, Docker, GitHub, and Render, the team developed, tested, and deployed a working web application that helps groups organize trips and make decisions in one place.
