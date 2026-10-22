# TripSync

TripSync is a collaborative group travel planning web application that helps users organize trips, manage itineraries, track expenses, make group decisions, and keep track of trip tasks in one place.

## Live Application

**TripSync:** https://tripsync-gw90.onrender.com

## Project Overview

TripSync was developed as a team software engineering project using Flask and SQLite. The application provides a centralized place for users and groups to plan and manage trips.

## Features

### 1. Creating and Organizing a Trip

**Persona:** Maya — Trip Organizer

**Scenario:** Maya is planning a trip to Miami with four friends. The group is using different group chats to discuss the trip, making it difficult to keep track of the destination, dates, and plans. Maya needs one place to organize the trip and invite her friends. She creates a trip in TripSync, enters the trip name, destination, travel dates, and budget, and invites friends who already have TripSync accounts.

**User Story:** As a trip organizer, I want to create a trip with its destination and travel dates so that I can organize the trip information in one place.

**Feature:** Create & Join Trips — Users can create trips and invite friends who already have TripSync accounts to join.

---

### 2. Planning the Group Itinerary

**Persona:** Jordan — Group Member

**Scenario:** Jordan and the group have several activities planned for their Miami trip. Their plans are being discussed through messages, making it easy to forget when or where activities are happening. Jordan needs a shared place where everyone can view the schedule. Jordan adds a dinner reservation to the TripSync itinerary with the restaurant, date, time, and location.

**User Story:** As a group member, I want to add activities to the shared itinerary so that everyone can see the group's plans.

**Feature:** Shared Trip Itinerary

---

### 3. Tracking Shared Expenses

**Persona:** Alexis — Budget-Conscious Traveler

**Scenario:** Alexis pays $200 for an activity that several group members participate in. Alexis wants the group to know how much was spent and who participated. Alexis records the expense in TripSync and enters the amount and participating group members so the group can keep track of its shared spending.

**User Story:** As a group member, I want to record a shared expense so that the group can keep track of its spending.

**Feature:** Trip Expense Tracker

---

### 4. Deciding on a Group Activity

**Persona:** Jordan — Group Member

**Scenario:** The group cannot decide whether to visit a museum or go on a boat tour. Everyone has a different preference, and discussing the options through group messages is becoming confusing. Jordan creates a vote in TripSync with the two activity options. Each group member submits a choice, and the group can view the results to help make the decision.

**User Story:** As a group member, I want to create a vote with different activity options so that the group can make decisions together.

**Feature:** Group Voting

---

### 5. Preparing for the Trip

**Persona:** Maya — Trip Organizer

**Scenario:** As the trip gets closer, Maya realizes that the group needs to complete tasks such as packing, buying tickets, and confirming reservations. She is worried that some tasks may be forgotten. Maya creates checklist items in TripSync and shares them with the group. Members mark items as completed so everyone can see what has been handled.

**User Story:** As a group member, I want to create checklist items so that important trip tasks are not forgotten.

**Feature:** Trip Checklist

---

### 6. Deleting a Trip

**Persona:** Maya — Trip Organizer

**Scenario:** Maya decides that a planned trip is no longer needed. Since she created the trip, she wants to remove it from TripSync along with the information associated with the trip. Maya selects the delete option and confirms the deletion. The trip and its related information are removed from the application for the group.

**User Story:** As a trip organizer, I want to delete a trip I created so that I can remove trips that are no longer needed.

**Feature:** Delete Trip

---

## User Authentication

TripSync provides user authentication so users can create an account, log in, log out, and access their saved trips through their dashboard.

Users must have a TripSync account before they can be added to an existing trip as a friend.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Git
- GitHub
- Render
- Docker

## Project Structure

```text

## Running TripSync Locally

### Requirements
- Python 3
- Git

### Installation
1. Clone the repository:
   `git clone https://github.com/jpitt2004/TripSync.git`
2. Open the project folder:
   `cd TripSync`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the application:
   `python app.py`
5. Open `http://127.0.0.1:5000` in a browser.

## Running TripSync with Docker

Make sure Docker Desktop is running.

1. Build the image:
   `docker build -t tripsync .`
2. Run the container:
   `docker run --rm -p 5000:5000 tripsync`
3. Open `http://localhost:5000`.

## Testing

TripSync includes automated tests and has also been manually tested.

Run the automated tests using:

`python -m unittest discover -s tests`

**Test result:** 10 automated tests passed during the final verification.

Manual testing included signup, login, trip creation, adding friends, itineraries, expenses, voting, checklists, trip deletion, and navigation.

## Deployment

TripSync is deployed on Render.

**Live application:** https://tripsync-gw90.onrender.com

To use the application, create an account, log in, and create a trip. Friends must register for their own TripSync accounts before they can be added to a shared trip.

**Storage limitation:** TripSync uses SQLite on Render. Because the deployed filesystem is temporary, saved accounts and trip information may be lost after a restart or redeployment.

TripSync/
│
├── app.py
├── database.db
├── README.md
├── TESTING.md
├── requirements.txt
├── Dockerfile
├── .dockerignore
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

