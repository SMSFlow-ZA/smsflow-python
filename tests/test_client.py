import unittest
from unittest.mock import Mock

from smsflow import SmsFlowClient


class FakeResponse:
    def __init__(self, body, status_code=200):
        self._body = body
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.content = b"{}"
        self.text = str(body)

    def json(self):
        return self._body


class SmsFlowClientTests(unittest.TestCase):
    def test_send_sms_authenticates_and_posts_payload(self):
        session = Mock()
        session.get.return_value = FakeResponse({"token": "token", "expiresInMinutes": 120, "schema": "Basic"})
        session.post.return_value = FakeResponse({"statusCode": 200, "sendResponse": {"eventId": 123}, "errors": None})

        client = SmsFlowClient(client_id="id", client_secret="secret", session=session)
        response = client.send_sms(
            campaign_name="Test",
            messages=[{"destination": "27000000000", "content": "Hello"}],
        )

        self.assertEqual(response["sendResponse"]["eventId"], 123)
        session.get.assert_called_once()
        session.post.assert_called_once()
        _, kwargs = session.post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")


if __name__ == "__main__":
    unittest.main()
