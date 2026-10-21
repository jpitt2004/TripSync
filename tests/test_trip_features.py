import unittest
import app


class TripFeatureTests(unittest.TestCase):

    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_dashboard_page(self):
        response = self.client.get("/dashboard")
        self.assertIn(response.status_code, [200, 302])

    def test_create_trip_page(self):
        response = self.client.get("/create-trip")
        self.assertIn(response.status_code, [200, 302])

    def test_add_friends_page(self):
        response = self.client.get("/add-friends")
        self.assertIn(response.status_code, [200, 302])


if __name__ == "__main__":
    unittest.main()
