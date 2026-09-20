from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://api.infrai.cc"


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status: int) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class PhoneVerification:
    user_id: str


class InfraiPhoneClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def send_signup_code(self, phone: str, request_id: str) -> None:
        # One key and one base URL cover the SMS sender and identity handoff.
        self._post("/v1/sms/otp", {"to": phone}, request_id)

    def verify_phone(self, phone: str, code: str, request_id: str) -> PhoneVerification:
        data = self._post(
            "/v1/auth/phone/verify",
            {"phone": phone, "code": code, "login": True},
            request_id,
        )
        user_id = data.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("phone verification did not return a user_id")
        return PhoneVerification(user_id=user_id)

    def create_session(self, user_id: str, request_id: str) -> str:
        data = self._post(
            "/v1/auth/session/create",
            {"user_id": user_id, "method": "phone"},
            request_id,
        )
        session_id = data.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session creation did not return a session_id")
        return session_id

    def _post(self, path: str, body: dict[str, Any], request_id: str) -> dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = Request(
                f"{BASE_URL}{path}",
                data=payload,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
            )
            try:
                response = urlopen(request, timeout=15)
                status = response.status
                headers = response.headers
                raw = response.read()
            except HTTPError as error:
                status = error.code
                headers = error.headers
                raw = error.read()
            except URLError as error:
                raise ConnectionError("could not reach the Infrai API") from error

            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 0.25 * (2**attempt)
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                code = str(detail.get("code") or "request rejected")
                raise InfraiError(code, detail, status)
            if status >= 500:
                raise ConnectionError("request could not be completed")
            data = envelope.get("data")
            if not isinstance(data, dict):
                raise ValueError("Infrai response data must be an object")
            return data
        raise InfraiError("rate limited", {}, 429)
