from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

try:
    import requests
except ImportError:  # pragma: no cover - exercised only when dependencies are not installed.
    requests = None


class SmsFlowError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


@dataclass
class _CachedAuth:
    token: str
    refresh_at: datetime


class SmsFlowClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        base_url: str = "https://portal.smsflow.co.za/",
        session: Any = None,
        timeout: int = 30,
    ) -> None:
        if not client_id or not client_secret:
            raise SmsFlowError("SMSFlow client_id and client_secret are required.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        if session is None and requests is None:
            raise SmsFlowError("The requests package is required when no custom session is supplied.")

        self.session = session or requests.Session()
        self.timeout = timeout
        self._cached_auth: _CachedAuth | None = None

    def authenticate(self) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/integration/authentication",
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout,
        )
        body = _read_body(response)

        if not response.ok:
            raise SmsFlowError("SMSFlow authentication failed.", status_code=response.status_code, body=body)

        token = body.get("token")
        expires_in = int(body.get("expiresInMinutes", 1))
        if not token:
            raise SmsFlowError("SMSFlow authentication did not return a token.")

        self._cached_auth = _CachedAuth(
            token=token,
            refresh_at=datetime.now(timezone.utc) + timedelta(minutes=max(expires_in - 5, 1)),
        )
        return body

    def send_sms(
        self,
        *,
        campaign_name: str,
        messages: Iterable[dict[str, str]],
        start_delivery_utc: str | None = None,
        check_opt_outs: bool = True,
    ) -> dict[str, Any]:
        message_list = list(messages)
        if not message_list:
            raise SmsFlowError("At least one SMS message is required.")

        response = self.session.post(
            f"{self.base_url}/api/integration/BulkMessages",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            json={
                "SendOptions": {
                    "startDeliveryUtc": start_delivery_utc,
                    "campaignName": campaign_name,
                    "checkOptOuts": check_opt_outs,
                },
                "messages": [
                    {
                        "content": message["content"],
                        "destination": message["destination"],
                    }
                    for message in message_list
                ],
            },
            timeout=self.timeout,
        )
        body = _read_body(response)

        if not response.ok:
            raise SmsFlowError("SMSFlow send failed.", status_code=response.status_code, body=body)

        return body

    def get_balance(self) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/integration/Balance",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=self.timeout,
        )
        body = _read_body(response)

        if not response.ok:
            raise SmsFlowError("SMSFlow balance request failed.", status_code=response.status_code, body=body)

        return body

    def _get_token(self) -> str:
        if self._cached_auth and datetime.now(timezone.utc) < self._cached_auth.refresh_at:
            return self._cached_auth.token

        auth = self.authenticate()
        return auth["token"]


def _read_body(response: Any) -> Any:
    if not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        return response.text
