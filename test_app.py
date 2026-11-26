import unittest
from unittest.mock import patch, MagicMock
import pymysql
from app import app, CODE_VERSION, GREETING

class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    def test_behaviour_and_identity(self):
        self.assertEqual(self.client.get("/").json,
                         {"greeting": GREETING, "version": CODE_VERSION})
        self.assertEqual(self.client.get("/version").json["version"], CODE_VERSION)
    def test_readiness_failure(self):
        with patch.dict("os.environ", {"FAIL_HEALTH": "true"}):
            self.assertEqual(self.client.get("/health").status_code, 503)
        with patch.dict("os.environ", {"FAIL_HEALTH": "false"}):
            self.assertEqual(self.client.get("/health").status_code, 200)
    @patch("app.pymysql.connect", side_effect=pymysql.OperationalError("example"))
    def test_dependency_failure_is_not_process_failure(self, _):
        with patch.dict("os.environ", {"DB_PASSWORD": "classroom"}):
            self.assertEqual(self.client.get("/db-time").status_code, 503)
            self.assertEqual(self.client.get("/health").status_code, 200)
    @patch("app.pymysql.connect")
    def test_database_query(self, connect):
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ["2026-01-01 12:00:00"]
        with patch.dict("os.environ", {"DB_PASSWORD": "classroom"}):
            response = self.client.get("/db-time")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["database_time"], "2026-01-01 12:00:00")
        cursor.execute.assert_called_once_with("SELECT NOW()")

if __name__ == "__main__":
    unittest.main()
