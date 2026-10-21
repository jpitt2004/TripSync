import unittest
import app


class AuthenticationTests(unittest.TestCase):

    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_signup_page(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get("/logout")
        self.assertIn(response.status_code, [200, 302])


if __name__ == "__main__":
    unittest.main()
