from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Any, Iterable

try:
    import requests
except ImportError:  # pragma: no cover - exercised only when dependencies are not installed.
    requests = None


class SmsFlowError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        body: Any = None,
        code: str = "SMSFLOW_ERROR",
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.code = code
        self.retryable = retryable


class SmsFlowAuthenticationError(SmsFlowError):
    pass


class SmsFlowValidationError(SmsFlowError):
    pass


class SmsFlowServerError(SmsFlowError):
    pass


class SmsFlowNetworkError(SmsFlowError):
    pass


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
        retry_retries: int = 0,
        retry_base_delay: float = 0.25,
        retry_max_delay: float = 2.0,
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
        self.retry_retries = retry_retries
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self._cached_auth: _CachedAuth | None = None

    def authenticate(self) -> dict[str, Any]:
        body = self._request(
            "get",
            f"{self.base_url}/api/integration/authentication",
            error_message="SMSFlow authentication failed.",
            allow_retry=True,
            auth=(self.client_id, self.client_secret),
        )

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
        retry: bool = False,
    ) -> dict[str, Any]:
        message_list = list(messages)
        if not message_list:
            raise SmsFlowValidationError("At least one SMS message is required.", code="MESSAGES_REQUIRED")

        return self._request(
            "post",
            f"{self.base_url}/api/integration/BulkMessages",
            error_message="SMSFlow send failed.",
            allow_retry=retry,
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
        )

    def get_balance(self) -> dict[str, Any]:
        return self._request(
            "get",
            f"{self.base_url}/api/integration/Balance",
            error_message="SMSFlow balance request failed.",
            allow_retry=True,
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )

    def _get_token(self) -> str:
        if self._cached_auth and datetime.now(timezone.utc) < self._cached_auth.refresh_at:
            return self._cached_auth.token

        auth = self.authenticate()
        return auth["token"]

    def _request(self, method: str, url: str, *, error_message: str, allow_retry: bool, **kwargs: Any) -> Any:
        attempts = (self.retry_retries + 1) if allow_retry else 1
        last_error: SmsFlowError | None = None

        for attempt in range(attempts):
            try:
                response = getattr(self.session, method)(url, timeout=self.timeout, **kwargs)
            except Exception as exc:  # requests exceptions or compatible custom session exceptions.
                error = SmsFlowNetworkError(
                    "SMSFlow request failed before a response was received.",
                    code="NETWORK_ERROR",
                    retryable=True,
                )
                error.__cause__ = exc
                last_error = error
            else:
                body = _read_body(response)
                if response.ok:
                    return body

                last_error = _create_api_error(error_message, response.status_code, body)

            if not last_error.retryable or attempt == attempts - 1:
                raise last_error

            sleep(_retry_delay_seconds(attempt, self.retry_base_delay, self.retry_max_delay))

        raise SmsFlowError("SMSFlow request failed.")


def _read_body(response: Any) -> Any:
    if not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        return response.text


def _create_api_error(message: str, status_code: int, body: Any) -> SmsFlowError:
    kwargs = {
        "status_code": status_code,
        "body": body,
        "code": _error_code_from_body(body),
        "retryable": _is_retryable_status(status_code),
    }

    if status_code == 401:
        return SmsFlowAuthenticationError(message, **kwargs)

    if 400 <= status_code < 500:
        return SmsFlowValidationError(message, **kwargs)

    return SmsFlowServerError(message, **kwargs)


def _error_code_from_body(body: Any) -> str:
    if isinstance(body, dict):
        errors = body.get("errors")
        if errors and isinstance(errors, list) and isinstance(errors[0], dict) and errors[0].get("code"):
            return str(errors[0]["code"])
        if body.get("code"):
            return str(body["code"])

    return "SMSFLOW_ERROR"


def _is_retryable_status(status_code: int) -> bool:
    return status_code in (408, 429) or status_code >= 500


def _retry_delay_seconds(attempt: int, base_delay: float, max_delay: float) -> float:
    return min(base_delay * (2**attempt), max_delay)
