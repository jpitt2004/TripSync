import unittest
import app


class TripPlanningTests(unittest.TestCase):

    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_itinerary_page(self):
        response = self.client.get("/itinerary")
        self.assertIn(response.status_code, [200, 302])

    def test_expenses_page(self):
        response = self.client.get("/expenses")
        self.assertIn(response.status_code, [200, 302])

    def test_voting_page(self):
        response = self.client.get("/voting")
        self.assertIn(response.status_code, [200, 302])

    def test_checklist_page(self):
        response = self.client.get("/checklist")
        self.assertIn(response.status_code, [200, 302])


if __name__ == "__main__":
    unittest.main()