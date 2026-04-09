import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from http.cookiejar import CookieJar
from typing import Any
from uuid import uuid4

import pytest


BASE_URL = os.getenv("FINTRACK_LIVE_BASE_URL")
MAILHOG_API_URL = os.getenv("FINTRACK_MAILHOG_API_URL", "http://127.0.0.1:8025/api/v2/messages")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not BASE_URL,
        reason="Set FINTRACK_LIVE_BASE_URL to run live integration smoke tests",
    ),
]


class LiveClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cookies = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))

    def _csrf_token(self) -> str | None:
        for cookie in self.cookies:
            if cookie.name == "csrf_token":
                return cookie.value
        return None

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        with_csrf: bool = False,
    ) -> tuple[int, dict[str, Any] | list[Any] | None]:
        headers = {"Accept": "application/json"}
        data = None

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if with_csrf:
            csrf_token = self._csrf_token()
            if not csrf_token:
                raise AssertionError("CSRF token cookie is missing")
            headers["X-CSRF-Token"] = csrf_token

        request = urllib.request.Request(
            url=f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with self.opener.open(request, timeout=15) as response:
                payload = response.read().decode("utf-8")
                parsed = json.loads(payload) if payload else None
                return response.status, parsed
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode("utf-8")
            parsed = json.loads(payload) if payload else None
            return exc.code, parsed


def _fetch_mailhog_messages() -> list[dict[str, Any]]:
    with urllib.request.urlopen(MAILHOG_API_URL, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("items", [])


def _decoded_message_body(message: dict[str, Any]) -> str:
    content = message.get("Content", {})
    raw_body = content.get("Body", "")
    headers = content.get("Headers", {})
    transfer_encoding = "".join(headers.get("Content-Transfer-Encoding", []))
    if "base64" in transfer_encoding.lower():
        return b64decode(raw_body).decode("utf-8", errors="ignore")
    return raw_body


def _extract_confirmation_token(messages: list[dict[str, Any]], email: str) -> str | None:
    token_pattern = re.compile(r"token=([0-9a-fA-F-]{36})")
    for message in reversed(messages):
        body = json.dumps(message)
        if email not in body:
            continue

        decoded_body = _decoded_message_body(message)
        match = token_pattern.search(decoded_body)
        if match:
            return match.group(1)
    return None


def _wait_for_confirmation_token(email: str, timeout_seconds: int = 30) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        token = _extract_confirmation_token(_fetch_mailhog_messages(), email)
        if token:
            return token
        time.sleep(1)
    raise AssertionError(f"Confirmation token for {email} was not found in MailHog")


def _extract_reset_token(messages: list[dict[str, Any]], email: str) -> str | None:
    token_pattern = re.compile(r"token=([^\"&\s<]+)")
    for message in reversed(messages):
        body = json.dumps(message)
        if email not in body:
            continue

        decoded_body = _decoded_message_body(message)
        if "/reset-password?token=" not in decoded_body:
            continue
        match = token_pattern.search(decoded_body)
        if match:
            return urllib.parse.unquote(match.group(1))
    return None


def _wait_for_reset_token(email: str, timeout_seconds: int = 30) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        token = _extract_reset_token(_fetch_mailhog_messages(), email)
        if token:
            return token
        time.sleep(1)
    raise AssertionError(f"Reset token for {email} was not found in MailHog")


def test_live_smoke_flow() -> None:
    assert BASE_URL is not None

    client = LiveClient(BASE_URL)
    email = f"smoke-{uuid4().hex[:12]}@example.com"
    password = "StrongPass123!"

    status_code, payload = client.request(
        "POST",
        "/auth/register",
        json_body={
            "email": email,
            "password": password,
            "first_name": "Smoke",
            "last_name": "Suite",
        },
    )
    assert status_code == 201, payload

    confirmation_token = _wait_for_confirmation_token(email)
    status_code, payload = client.request(
        "POST",
        "/email/confirm",
        json_body={
            "email": email,
            "confirmation_token": confirmation_token,
        },
    )
    assert status_code == 200, payload

    status_code, payload = client.request(
        "POST",
        "/auth/login",
        json_body={
            "email": email,
            "password": password,
        },
    )
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload["token_type"] == "bearer"
    assert client._csrf_token() is not None

    status_code, payload = client.request("GET", "/users/profile")
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload["email"] == email

    status_code, income_category = client.request(
        "POST",
        "/categories/",
        json_body={"name": "Salary", "type": "income"},
        with_csrf=True,
    )
    assert status_code == 201, income_category
    assert isinstance(income_category, dict)

    status_code, expense_category = client.request(
        "POST",
        "/categories/",
        json_body={"name": "Food", "type": "expense"},
        with_csrf=True,
    )
    assert status_code == 201, expense_category
    assert isinstance(expense_category, dict)

    status_code, payload = client.request(
        "POST",
        "/transactions/",
        json_body={
            "category_id": income_category["id"],
            "amount": 500000,
            "description": "Monthly salary",
            "occurred_at": "2026-04-06T09:00:00Z",
        },
        with_csrf=True,
    )
    assert status_code == 201, payload

    status_code, payload = client.request(
        "POST",
        "/transactions/",
        json_body={
            "category_id": expense_category["id"],
            "amount": 25000,
            "description": "Groceries",
            "occurred_at": "2026-04-06T12:00:00Z",
        },
        with_csrf=True,
    )
    assert status_code == 201, payload

    status_code, payload = client.request(
        "POST",
        "/budgets/",
        json_body={
            "category_id": expense_category["id"],
            "limit_amount": 100000,
            "period_start": "2026-04-01",
            "period_end": "2026-04-30",
        },
        with_csrf=True,
    )
    assert status_code == 201, payload

    status_code, payload = client.request("GET", "/budgets/progress")
    assert status_code == 200, payload
    assert isinstance(payload, list)
    assert payload[0]["spent_amount"] == "25000.00"
    assert payload[0]["remaining_amount"] == "75000.00"
    assert payload[0]["utilization_percent"] == 25.0

    status_code, payload = client.request("GET", "/analytics/summary")
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload == {
        "income": "500000.00",
        "expense": "25000.00",
        "balance": "475000.00",
    }

    query = urllib.parse.urlencode({"date_from": "2026-04-01", "date_to": "2026-04-30"})
    status_code, payload = client.request("GET", f"/reports/overview?{query}")
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload["summary"]["balance"] == "475000.00"
    assert len(payload["by_category"]) == 2
    assert payload["budgets"][0]["spent_amount"] == "25000.00"

    status_code, payload = client.request("POST", "/auth/refresh", with_csrf=True)
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload["token_type"] == "bearer"

    status_code, payload = client.request("POST", "/auth/logout", with_csrf=True)
    assert status_code == 200, payload
    assert payload == {"message": "You have been logged out"}

    status_code, payload = client.request("GET", "/users/profile")
    assert status_code == 401, payload
    assert isinstance(payload, dict)
    detail = str(payload["detail"]).lower()
    assert "token" in detail or "токен" in detail


def test_live_password_reset_flow() -> None:
    assert BASE_URL is not None

    client = LiveClient(BASE_URL)
    email = f"reset-{uuid4().hex[:12]}@example.com"
    password = "StrongPass123!"
    new_password = "EvenStronger456!"

    status_code, payload = client.request(
        "POST",
        "/auth/register",
        json_body={
            "email": email,
            "password": password,
            "first_name": "Reset",
            "last_name": "Suite",
        },
    )
    assert status_code == 201, payload

    confirmation_token = _wait_for_confirmation_token(email)
    status_code, payload = client.request(
        "POST",
        "/email/confirm",
        json_body={
            "email": email,
            "confirmation_token": confirmation_token,
        },
    )
    assert status_code == 200, payload

    status_code, payload = client.request(
        "POST",
        "/auth/login",
        json_body={
            "email": email,
            "password": password,
        },
    )
    assert status_code == 200, payload

    status_code, payload = client.request("GET", "/users/profile")
    assert status_code == 200, payload

    status_code, payload = client.request(
        "POST",
        "/auth/forgot-password",
        json_body={"email": email},
    )
    assert status_code == 200, payload

    reset_token = _wait_for_reset_token(email)
    status_code, payload = client.request(
        "POST",
        "/auth/reset-password",
        json_body={
            "token": reset_token,
            "new_password": new_password,
        },
    )
    assert status_code == 200, payload

    # Old authenticated session should no longer be usable after password reset.
    status_code, payload = client.request("GET", "/users/profile")
    assert status_code == 401, payload

    fresh_client = LiveClient(BASE_URL)
    status_code, payload = fresh_client.request(
        "POST",
        "/auth/login",
        json_body={
            "email": email,
            "password": password,
        },
    )
    assert status_code == 401, payload

    status_code, payload = fresh_client.request(
        "POST",
        "/auth/login",
        json_body={
            "email": email,
            "password": new_password,
        },
    )
    assert status_code == 200, payload

    status_code, payload = fresh_client.request("GET", "/users/profile")
    assert status_code == 200, payload
    assert isinstance(payload, dict)
    assert payload["email"] == email


def test_live_resend_confirmation_endpoint_is_reachable() -> None:
    assert BASE_URL is not None

    client = LiveClient(BASE_URL)
    email = f"resend-{uuid4().hex[:12]}@example.com"
    password = "StrongPass123!"

    status_code, payload = client.request(
        "POST",
        "/auth/register",
        json_body={
            "email": email,
            "password": password,
            "first_name": "Resend",
            "last_name": "Suite",
        },
    )
    assert status_code == 201, payload

    status_code, payload = client.request(
        "POST",
        "/email/resend",
        json_body={"email": email},
    )
    assert status_code == 429, payload
    assert isinstance(payload, dict)
    detail = str(payload["detail"]).lower()
    assert "too many" in detail or "част" in detail
