"""
conftest.py — Global fixtures available to ALL test files automatically.
No imports needed in test files; pytest discovers these automatically.
"""

import pytest
import requests


# ── Base URL fixture ──────────────────────────────────────────────────────────
# Using Restful-Booker: a free, public API built for QA practice
# Docs: https://restful-booker.herokuapp.com/apidoc/index.html

@pytest.fixture(scope="session")
def base_url():
    """Returns the base URL for the API under test. Session-scoped = created once per test run."""
    return "https://restful-booker.herokuapp.com"


# ── HTTP Session fixture ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_session():
    """
    Creates a requests.Session() once for the entire test run.
    A Session reuses the underlying TCP connection — faster than creating
    a new connection per test.
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session          # ← hands the session to the test
    session.close()        # ← teardown: runs after ALL tests finish


# ── Auth token fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def auth_token(api_session, base_url):
    """
    Logs in once and returns the auth token.
    Session-scoped = login happens once, token is reused across all tests.
    Depends on: api_session, base_url  ← pytest injects these automatically.
    """
    payload = {
        "username": "admin",
        "password": "password123"
    }
    response = api_session.post(f"{base_url}/auth", json=payload)
    assert response.status_code == 200, f"Auth failed: {response.text}"

    token = response.json().get("token")
    assert token, "Token was empty — login may have failed"
    return token


# ── Booking payload fixture ───────────────────────────────────────────────────

@pytest.fixture
def sample_booking_payload():
    """
    Returns a valid booking payload dict.
    Function-scoped (default) = fresh copy for each test that requests it.
    """
    return {
        "firstname": "Chaitra",
        "lastname": "Anand",
        "totalprice": 200,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-01",
            "checkout": "2026-06-10"
        },
        "additionalneeds": "Breakfast"
    }


# ── Created booking fixture (with teardown) ───────────────────────────────────

@pytest.fixture
def created_booking(api_session, base_url, sample_booking_payload, auth_token):
    """
    Creates a booking before the test, yields its ID to the test,
    then DELETES it after the test completes — clean teardown.

    This pattern is called 'setup → yield → teardown' and is one of
    pytest's most powerful features vs. TestNG @BeforeMethod/@AfterMethod.
    """
    # SETUP: create a booking
    response = api_session.post(
        f"{base_url}/booking",
        json=sample_booking_payload
    )
    assert response.status_code == 200, f"Failed to create booking: {response.text}"
    booking_id = response.json()["bookingid"]

    yield booking_id       # ← test receives the booking ID here

    # TEARDOWN: delete the booking after the test (even if test fails)
    api_session.delete(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={auth_token}"}
    )
