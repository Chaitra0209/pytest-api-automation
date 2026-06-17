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

    """
conftest_reporting_additions.py — Day 3 (Part 2)

These are ADDITIONS to your existing conftest.py — append this content
to the bottom of your current conftest.py file. Do not replace the
whole file; your existing fixtures (api_session, base_url, auth_token,
etc.) must stay.

New concepts introduced:
  - pytest_html_report_title  : custom title on the HTML report
  - pytest_configure          : adds environment metadata to the report
  - pytest_html_results_summary : adds a custom summary section
  - hookimpl for capturing extra info on test failure
"""

import pytest


# ── Custom report title ────────────────────────────────────────────────────────

def pytest_html_report_title(report):
    """Changes the <title> and main heading of the generated HTML report."""
    report.title = "QA Automation Report — pytest-api-automation (Chaitra Anand)"


# ── Add environment metadata (shows at top of HTML report) ─────────────────────

def pytest_configure(config):
    """
    Adds an 'Environment' table to the top of the HTML report.
    Useful in real projects to record which API/environment was tested,
    browser version, build number, etc. — exactly what interviewers expect
    to see in a professional test report.
    """
    if hasattr(config, "_metadata"):
        config._metadata["Project"] = "pytest-api-automation"
        config._metadata["API Under Test"] = "Restful-Booker (restful-booker.herokuapp.com)"
        config._metadata["Tester"] = "Chaitra Anand"
        config._metadata["Test Type"] = "API Automation (pytest + requests)"


# ── Custom summary section in the HTML report ───────────────────────────────────

def pytest_html_results_summary(prefix, summary, postfix):
    """
    Adds a custom note block right above the results table in the HTML report.
    """
    prefix.extend([
        "<p><strong>Note:</strong> This suite covers Auth, Booking GET/POST/PUT/PATCH "
        "endpoints. One known defect is documented and marked xfail "
        "(see test_bookings_post.py). See README.md / TEST_NOTES.md for full defect "
        "list and coverage summary.</p>"
    ])


# ── Capture extra failure context (appears in report when a test fails) ────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    When a test fails, this attaches the actual HTTP response (if available)
    to the HTML report row, so you don't have to dig through terminal logs
    to see what the API actually returned.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # If the test stored a 'last_response' attribute on itself, show it
        extra = getattr(report, "extra", [])
        if hasattr(item, "_last_response_text"):
            from pytest_html import extras
            extra.append(extras.text(item._last_response_text, name="Last API Response"))
            report.extra = extra

