"""
tests/test_auth.py — Day 1

Tests for the /auth endpoint (token generation).
This is the simplest starting point — just POST credentials, check response.

API docs: https://restful-booker.herokuapp.com/apidoc/index.html#api-Auth
"""

import pytest


# ── Happy Path ────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
def test_auth_with_valid_credentials_returns_token(api_session, base_url):
    """
    GIVEN valid admin credentials
    WHEN POST /auth is called
    THEN response is 200 and a non-empty token is returned
    """
    payload = {"username": "admin", "password": "password123"}

    response = api_session.post(f"{base_url}/auth", json=payload)

    # Assert status code
    assert response.status_code == 200, (
        f"Expected 200 but got {response.status_code}. Body: {response.text}"
    )

    # Assert token exists and is a non-empty string
    body = response.json()
    assert "token" in body, "Response body missing 'token' key"
    assert isinstance(body["token"], str), "Token should be a string"
    assert len(body["token"]) > 0, "Token should not be empty"


@pytest.mark.smoke
@pytest.mark.api
def test_auth_response_time_is_acceptable(api_session, base_url):
    """
    GIVEN a valid auth request
    WHEN the response is received
    THEN it should arrive within 3 seconds (basic performance check)
    """
    payload = {"username": "admin", "password": "password123"}

    response = api_session.post(f"{base_url}/auth", json=payload)

    elapsed = response.elapsed.total_seconds()
    assert elapsed < 3.0, f"Auth response too slow: {elapsed:.2f}s (threshold: 3s)"


# ── Negative Path ─────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.api
def test_auth_with_wrong_password_returns_reason(api_session, base_url):
    """
    GIVEN wrong password
    WHEN POST /auth is called
    THEN response contains 'reason' key (not a token)
    """
    payload = {"username": "admin", "password": "wrongpassword"}

    response = api_session.post(f"{base_url}/auth", json=payload)

    body = response.json()
    # Restful-Booker returns {"reason": "Bad credentials"} on failure
    assert "reason" in body, (
        f"Expected 'reason' key in body for bad credentials. Got: {body}"
    )
    assert "token" not in body, "Should NOT return a token for bad credentials"


@pytest.mark.regression
@pytest.mark.api
def test_auth_with_empty_credentials_returns_reason(api_session, base_url):
    """
    GIVEN empty username and password
    WHEN POST /auth is called
    THEN response contains 'reason' key, no token issued
    """
    payload = {"username": "", "password": ""}

    response = api_session.post(f"{base_url}/auth", json=payload)

    body = response.json()
    assert "reason" in body, f"Expected error reason for empty credentials. Got: {body}"
    assert "token" not in body, "Should NOT return a token for empty credentials"


@pytest.mark.regression
@pytest.mark.api
def test_auth_with_missing_fields_does_not_crash(api_session, base_url):
    """
    GIVEN a payload with missing fields
    WHEN POST /auth is called
    THEN the API handles it gracefully (does not return 500)
    """
    payload = {}   # completely empty payload

    response = api_session.post(f"{base_url}/auth", json=payload)

    # Should not be a server crash
    assert response.status_code != 500, (
        f"API crashed with 500 on empty payload. Body: {response.text}"
    )
