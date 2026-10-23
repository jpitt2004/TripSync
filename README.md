# TripSync

TripSync is a collaborative group travel planning web application that helps users organize trips, manage itineraries, track expenses, make group decisions, and complete trip tasks in one centralized platform.

## Live Application

**Live Website:** https://tripsync-gw90.onrender.com

**GitHub Repository:** https://github.com/jpitt2004/TripSync

## Project Overview

TripSync was developed as a team software engineering project using Python, Flask, and Neon PostgreSQL.

The application provides a centralized platform where users and groups can plan trips, organize activities, track shared expenses, vote on group decisions, and manage checklists.

Instead of relying on multiple group chats, notes, and applications, users can organize important trip information through one website.

TripSync uses a PostgreSQL database hosted by Neon to provide persistent storage for user accounts, trips, and related information. The application is containerized with Docker and deployed to Render.

## Features

### 1. Creating and Organizing a Trip

**Persona:** Maya — Trip Organizer

**Scenario:** Maya is planning a trip to Miami with four friends. The group is using different group chats to discuss the trip, making it difficult to keep track of the destination, dates, and plans. Maya needs one place to organize the trip and invite her friends. She creates a trip in TripSync, enters the trip name, destination, travel dates, and budget, and invites her friends to participate.

**User Story:** As a trip organizer, I want to create a trip with its destination and travel dates so that I can organize the trip information in one place.

**Feature:** Create & Join Trips — Users can create trips, invite friends, and access shared trip information.

---

### 2. Planning the Group Itinerary

**Persona:** Jordan — Group Member

**Scenario:** Jordan and the group have several activities planned for their Miami trip. Their plans are being discussed through messages, making it easy to forget when or where activities are happening. Jordan needs a shared place where everyone can view the schedule. Jordan adds a dinner reservation to the TripSync itinerary with the restaurant, date, time, and location.

**User Story:** As a group member, I want to add activities to the shared itinerary so that everyone can see the group's plans.

**Feature:** Shared Trip Itinerary — Group members can add and view trip activities, including activity details, dates, times, and locations.

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

**Feature:** Group Voting — Members can create polls, submit votes, and view voting results.

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

TripSync includes user authentication to protect accounts and trip information.

Users can:

- Create an account
- Log in with their credentials
- Log out securely
- Access their personal trip dashboard
- Create and manage trips
- Invite friends to participate in trips
- Access shared trip information

### Friend Invitations

TripSync supports adding registered users to trips.

If an invitation is created for someone who has not registered yet, the application can store a pending invitation. When that person registers using the invited information, the pending invitation can be processed and the person added to the trip.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Flask | Web application framework |
| PostgreSQL | Relational database |
| Neon | Cloud-hosted PostgreSQL database |
| Psycopg | Python PostgreSQL database adapter |
| HTML | Website structure |
| CSS | Website styling |
| JavaScript | Frontend functionality |
| Git | Version control |
| GitHub | Source code repository and collaboration |
| Docker | Application containerization |
| Render | Cloud application hosting |
| python-dotenv | Local environment variable configuration |

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

**Note:** The project also uses a local `.env` file to store environment variables during development. This file is excluded from Git and Docker to protect database credentials and application secrets.

TripSync's current application data is stored in Neon PostgreSQL rather than a local SQLite database.

## Running TripSync Locally

### Requirements

Before running TripSync locally, install:

- Python 3
- Git
- Required Python packages listed in `requirements.txt`
- Access to a PostgreSQL database, such as Neon

### Installation

**Step 1: Clone the repository.**

```bash
git clone https://github.com/jpitt2004/TripSync.git
```

**Step 2: Navigate to the project folder.**

```bash
cd TripSync
```

**Step 3: Create a virtual environment.**

```bash
python -m venv .venv
```

**Step 4: Activate the virtual environment.**

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

**Step 5: Install the required dependencies.**

```bash
pip install -r requirements.txt
```

**Step 6: Configure environment variables.**

Create a file named `.env` in the project folder.

Add the following variables:

```dotenv
DATABASE_URL=your_neon_postgresql_connection_string
SECRET_KEY=your_secure_random_secret_key
```

Replace the example values with your own database connection string and a securely generated secret key.

The `DATABASE_URL` variable connects the application to PostgreSQL.

The `SECRET_KEY` variable is used by Flask to protect session information.

**Important:** Never upload your `.env` file, database credentials, or secret key to GitHub.

**Step 7: Start the Flask application.**

```bash
python app.py
```

**Step 8: Open the application in your browser.**

http://127.0.0.1:5000

Once the application opens, create an account, log in, and begin planning a trip.

**Database setup:** The PostgreSQL database must already contain the tables required by TripSync. The application does not automatically create the full database schema when it starts.

## Running TripSync with Docker

TripSync can also run inside a Docker container.

Make sure Docker Desktop is installed and running.

**Step 1: Build the Docker image.**

```bash
docker build -t tripsync .
```

**Step 2: Run the Docker container with environment variables.**

Make sure your `.env` file has been created with valid database credentials.

```bash
docker run --rm -p 5000:5000 --env-file .env tripsync
```

**Step 3: Open the application.**

http://localhost:5000

The application will run inside the Docker container and connect to the configured PostgreSQL database.

Press `Ctrl + C` in the terminal to stop the container.

## Testing

TripSync includes automated tests and has also undergone manual testing.

### Automated Testing

The project includes test files for authentication, trip features, and trip planning.

Run the automated tests using:

```bash
python -m unittest discover -s tests
```

**Note:** Automated tests should be verified against the current PostgreSQL implementation. Results from earlier SQLite-based testing do not automatically establish that every test still passes after the database migration.

### Manual Testing

The following functionality has been manually tested during development:

- User registration and login
- Creating trips
- Adding friends and processing pending invitations
- Viewing trip information
- Adding itinerary activities
- Recording expenses
- Creating and participating in votes
- Creating and completing checklist items
- Deleting trips as the owner
- Navigating between application pages

### Live Deployment Testing

After deployment to Render with Neon PostgreSQL, the following tests were completed successfully:

- Logging in using an existing Neon account
- Creating a new trip on the live website
- Refreshing the dashboard and confirming the trip remained saved
- Restarting the Render service and confirming the trip remained saved
- Deleting the test trip

These tests verified that the deployed application could access persistent trip data through Neon PostgreSQL.

Additional testing documentation is available in `TESTING.md`.

## Deployment

TripSync is containerized using Docker and deployed to Render.

**Live Application:** https://tripsync-gw90.onrender.com

**Source Code:** https://github.com/jpitt2004/TripSync

### Deployment Configuration

The application uses:

- **GitHub** to store and manage source code
- **Docker** to package the application and install dependencies
- **Render** to host the Flask application
- **Neon PostgreSQL** to store application data persistently

The following environment variables are configured on Render:

```text
DATABASE_URL
SECRET_KEY
```

These values are stored as environment variables rather than being written directly into the source code.

### Persistent Database Storage

TripSync uses Neon PostgreSQL for persistent database storage.

User accounts, trip information, itinerary activities, expenses, voting information, and checklist items are stored in PostgreSQL.

Unlike the previous SQLite implementation on Render's temporary filesystem, Neon stores database information separately from the web service.

This allows saved information to remain available after the application restarts or redeploys, subject to the database service remaining available.

## Team Members

- Jeniya Pittman
- JaDaeyah Murray
- Brandon Howell

## Future Improvements

Possible improvements include:

- Email notifications for trip invitations
- Automatic expense splitting between participants
- Improved mobile responsiveness
- Additional trip customization options
- Calendar integration for trip activities
- Enhanced notifications for itinerary changes and group decisions

## Conclusion

TripSync demonstrates how software engineering concepts can be applied to develop a collaborative travel planning application.

Through Python, Flask, Neon PostgreSQL, Docker, GitHub, and Render, the team developed, tested, and deployed a web application that helps groups organize trips, track expenses, plan activities, and make decisions in one place.

The project incorporates user authentication, shared trip management, database integration, version control, testing, and cloud deployment.

Migrating from SQLite to Neon PostgreSQL also improved the application's ability to retain data across Render service restarts, making TripSync more suitable for ongoing use and demonstration.
