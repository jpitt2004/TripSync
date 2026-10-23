# TripSync Testing Report

## Testing Overview

TripSync was tested using automated route tests and manual feature testing to verify that the application's major functions operate correctly.

Testing was performed on the local Flask application and the deployed application hosted on Render using Neon PostgreSQL.

## Automated Testing

Automated tests were executed using Python's built-in unittest framework.

**Command:**

```powershell
python -m unittest discover -s tests -v
```

**Results:** 10 tests passed.

| Test | Result |
|---|---|
| Login page | Passed |
| Logout | Passed |
| Signup page | Passed |
| Add friends page | Passed |
| Create trip page | Passed |
| Dashboard page | Passed |
| Checklist page | Passed |
| Expenses page | Passed |
| Itinerary page | Passed |
| Voting page | Passed |

All 10 automated tests completed successfully.

These tests verify application route behavior but do not provide complete coverage of database operations or every user interaction.

## Manual Feature Testing

The following features were tested manually during development:

| Feature | Result |
|---|---|
| User registration and login | Passed |
| Create a trip | Passed |
| Add friends and process pending invitations | Passed |
| Shared itinerary | Passed |
| Expense tracker | Passed |
| Group voting | Passed |
| Trip checklist | Passed |
| Delete a trip | Passed |
| Application navigation | Passed |

## Neon PostgreSQL Testing

TripSync was migrated from SQLite to Neon PostgreSQL to support persistent database storage.

The following database-related functions were successfully tested locally:

- User registration and authentication
- Creating trips
- Adding itinerary activities
- Recording expenses
- Creating polls and saving votes
- Creating and updating checklist items
- Processing pending invitations
- Deleting trips

## Live Deployment Testing

The application was deployed to Render and connected to Neon PostgreSQL.

**Live Application:** https://tripsync-gw90.onrender.com

The following live tests were completed successfully:

1. Logged in using an existing Neon test account.
2. Created a new trip through the deployed application.
3. Refreshed the dashboard and confirmed that the trip remained saved.
4. Restarted the Render service.
5. Logged back into the application and confirmed that the trip remained saved.
6. Deleted the test trip successfully.

These results demonstrate that TripSync can save and retrieve trip information from Neon PostgreSQL and retain it across a Render service restart.

## Conclusion

TripSync successfully passed all 10 automated route tests and the manual feature tests performed during development.

The live deployment also demonstrated successful PostgreSQL connectivity and persistent trip storage.

Although additional testing could improve coverage of security, edge cases, and database operations, the completed tests provide evidence that the application's core features function as intended.