import unittest
from unittest.mock import Mock

from smsflow import SmsFlowAuthenticationError, SmsFlowClient, SmsFlowValidationError


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

    def test_send_sms_raises_typed_validation_error(self):
        session = Mock()
        session.get.return_value = FakeResponse({"token": "token", "expiresInMinutes": 120, "schema": "Basic"})
        session.post.return_value = FakeResponse(
            {"statusCode": 400, "errors": [{"code": "INVALID_DESTINATION", "message": "Invalid destination."}]},
            status_code=400,
        )

        client = SmsFlowClient(client_id="id", client_secret="secret", session=session)

        with self.assertRaises(SmsFlowValidationError) as context:
            client.send_sms(
                campaign_name="Test",
                messages=[{"destination": "not-a-number", "content": "Hello"}],
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.code, "INVALID_DESTINATION")
        self.assertFalse(context.exception.retryable)

    def test_authenticate_retries_temporary_server_failures(self):
        session = Mock()
        session.get.side_effect = [
            FakeResponse({"errors": [{"code": "SERVICE_UNAVAILABLE"}]}, status_code=503),
            FakeResponse({"token": "token", "expiresInMinutes": 120, "schema": "Basic"}),
        ]

        client = SmsFlowClient(
            client_id="id",
            client_secret="secret",
            session=session,
            retry_retries=1,
            retry_base_delay=0,
        )

        response = client.authenticate()

        self.assertEqual(response["token"], "token")
        self.assertEqual(session.get.call_count, 2)

    def test_authenticate_raises_typed_authentication_error(self):
        session = Mock()
        session.get.return_value = FakeResponse(
            {"errors": [{"code": "AUTHENTICATION_FAILED", "message": "Invalid credentials."}]},
            status_code=401,
        )

        client = SmsFlowClient(client_id="id", client_secret="secret", session=session)

        with self.assertRaises(SmsFlowAuthenticationError) as context:
            client.authenticate()

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.code, "AUTHENTICATION_FAILED")


if __name__ == "__main__":
    unittest.main()
