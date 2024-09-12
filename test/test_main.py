import json
import unittest

from fastapi.testclient import TestClient

from app import create_app


class MainBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.client = TestClient(self.app)
        self.domain = "http://localhost"

    def test_is_open_now(self):
        rv = self.client.get(
            f"{self.app.state.config.get('BASE_URI')}/is-open-now/",
        )
        self.assertEqual(rv.status_code, 200)
        response_json = json.loads(rv.text)
        self.assertIsInstance(response_json, bool)

    def test_today(self):
        rv = self.client.get(
            f"{self.app.state.config.get('BASE_URI')}/today/",
        )
        self.assertEqual(rv.status_code, 200)
        response_json = json.loads(rv.text)
        self.assertIn("open", response_json)
        self.assertIsInstance(response_json["open"], str)
        self.assertIn("close", response_json)
        self.assertIsInstance(response_json["close"], str)

    def test_next_open(self):
        rv = self.client.get(
            f"{self.app.state.config.get('BASE_URI')}/next-open/",
        )
        self.assertEqual(rv.status_code, 200)
        response_json = json.loads(rv.text)
        self.assertIn("open", response_json)
        self.assertIsInstance(response_json["open"], str)
        self.assertIn("close", response_json)
        self.assertIsInstance(response_json["close"], str)
        self.assertIn("day", response_json)
        self.assertIsInstance(response_json["day"], str)
        self.assertIn("day_alt", response_json)
        self.assertIsInstance(response_json["day_alt"], str)
