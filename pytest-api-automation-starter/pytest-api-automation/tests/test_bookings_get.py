"""
tests/test_bookings_get.py — Day 1 / Day 2

Tests for GET /booking and GET /booking/{id} endpoints.
Introduces:
  - @pytest.mark.parametrize  (data-driven tests)
  - created_booking fixture    (setup + teardown)
  - Response schema validation (checking all expected keys exist)

API docs: https://restful-booker.herokuapp.com/apidoc/index.html#api-Booking
"""

import pytest


# ── GET /booking (list all) ───────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
def test_get_all_bookings_returns_list(api_session, base_url):
    """
    GIVEN the bookings endpoint
    WHEN GET /booking is called
    THEN response is 200 and body is a non-empty list
    """
    response = api_session.get(f"{base_url}/booking")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list), f"Expected list, got {type(body)}"
    assert len(body) > 0, "Expected at least one booking to exist"


@pytest.mark.smoke
@pytest.mark.api
def test_get_all_bookings_each_item_has_bookingid(api_session, base_url):
    """
    GIVEN the bookings list response
    WHEN each item is inspected
    THEN every item contains a 'bookingid' integer key
    """
    response = api_session.get(f"{base_url}/booking")
    bookings = response.json()

    for item in bookings:
        assert "bookingid" in item, f"Item missing 'bookingid': {item}"
        assert isinstance(item["bookingid"], int), (
            f"bookingid should be int, got {type(item['bookingid'])}"
        )


# ── GET /booking with filters ─────────────────────────────────────────────────

@pytest.mark.parametrize("firstname, lastname", [
    ("Sally",  "Brown"),
    ("Foo",    "Bar"),
    ("James",  "Brown"),
])
@pytest.mark.regression
@pytest.mark.api
def test_filter_bookings_by_name(api_session, base_url, firstname, lastname):
    """
    GIVEN name filter params
    WHEN GET /booking?firstname=X&lastname=Y is called
    THEN response is 200 (even if list is empty — filter itself should not error)

    This is a parametrized test — it runs 3 times, once per name pair above.
    Equivalent to a data-driven test in TestNG with @DataProvider.
    """
    response = api_session.get(
        f"{base_url}/booking",
        params={"firstname": firstname, "lastname": lastname}
    )

    assert response.status_code == 200, (
        f"Filter by name failed for {firstname} {lastname}: {response.text}"
    )
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("checkin, checkout", [
    ("2026-01-01", "2026-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2024-06-01", "2024-06-30"),
])
@pytest.mark.regression
@pytest.mark.api
def test_filter_bookings_by_date_range(api_session, base_url, checkin, checkout):
    """
    GIVEN date range filter params
    WHEN GET /booking?checkin=X&checkout=Y is called
    THEN response is 200 for each date range
    """
    response = api_session.get(
        f"{base_url}/booking",
        params={"checkin": checkin, "checkout": checkout}
    )

    assert response.status_code == 200, (
        f"Date filter failed for {checkin}–{checkout}: {response.text}"
    )


# ── GET /booking/{id} ─────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
def test_get_booking_by_id_returns_correct_schema(api_session, base_url, created_booking):
    """
    GIVEN an existing booking ID (created and cleaned up by created_booking fixture)
    WHEN GET /booking/{id} is called
    THEN response is 200 and all expected fields are present
    """
    booking_id = created_booking   # fixture creates the booking, gives us its ID

    response = api_session.get(f"{base_url}/booking/{booking_id}")

    assert response.status_code == 200, (
        f"Expected 200 for booking {booking_id}, got {response.status_code}"
    )

    body = response.json()

    # Schema check — all expected keys must be present
    expected_keys = ["firstname", "lastname", "totalprice",
                     "depositpaid", "bookingdates", "additionalneeds"]
    for key in expected_keys:
        assert key in body, f"Response missing expected key: '{key}'. Body: {body}"

    # bookingdates sub-object check
    assert "checkin" in body["bookingdates"], "bookingdates missing 'checkin'"
    assert "checkout" in body["bookingdates"], "bookingdates missing 'checkout'"


@pytest.mark.regression
@pytest.mark.api
def test_get_booking_by_id_returns_correct_values(api_session, base_url,
                                                   created_booking,
                                                   sample_booking_payload):
    """
    GIVEN a booking created with known payload
    WHEN GET /booking/{id} is called
    THEN returned values match what was sent during creation
    """
    booking_id = created_booking

    response = api_session.get(f"{base_url}/booking/{booking_id}")
    body = response.json()

    assert body["firstname"] == sample_booking_payload["firstname"]
    assert body["lastname"] == sample_booking_payload["lastname"]
    assert body["totalprice"] == sample_booking_payload["totalprice"]
    assert body["depositpaid"] == sample_booking_payload["depositpaid"]


@pytest.mark.regression
@pytest.mark.api
def test_get_nonexistent_booking_returns_404(api_session, base_url):
    """
    GIVEN a booking ID that does not exist
    WHEN GET /booking/{id} is called
    THEN response is 404
    """
    nonexistent_id = 9999999

    response = api_session.get(f"{base_url}/booking/{nonexistent_id}")

    assert response.status_code == 404, (
        f"Expected 404 for nonexistent booking, got {response.status_code}"
    )
