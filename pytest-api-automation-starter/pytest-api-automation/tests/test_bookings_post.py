"""
tests/test_bookings_post.py — Day 2 (Part 1)

Tests for POST /booking (create a new booking).
Reuses fixtures already defined in conftest.py — no new setup needed.

API docs: https://restful-booker.herokuapp.com/apidoc/index.html#api-Booking
"""

import pytest


# ── Happy Path ────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
def test_create_booking_returns_201_or_200_with_booking_id(api_session, base_url,
                                                             sample_booking_payload):
    """
    GIVEN a valid booking payload
    WHEN POST /booking is called
    THEN response is 200 and contains a 'bookingid'
    """
    response = api_session.post(f"{base_url}/booking", json=sample_booking_payload)

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Body: {response.text}"
    )

    body = response.json()
    assert "bookingid" in body, f"Response missing 'bookingid'. Body: {body}"
    assert isinstance(body["bookingid"], int), "bookingid should be an integer"


@pytest.mark.smoke
@pytest.mark.api
def test_create_booking_echoes_submitted_data(api_session, base_url,
                                                sample_booking_payload):
    """
    GIVEN a booking payload with known values
    WHEN POST /booking is called
    THEN the response 'booking' object matches what was submitted
    """
    response = api_session.post(f"{base_url}/booking", json=sample_booking_payload)
    body = response.json()

    returned_booking = body["booking"]
    assert returned_booking["firstname"] == sample_booking_payload["firstname"]
    assert returned_booking["lastname"] == sample_booking_payload["lastname"]
    assert returned_booking["totalprice"] == sample_booking_payload["totalprice"]
    assert returned_booking["depositpaid"] == sample_booking_payload["depositpaid"]


# ── Negative Path ─────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.api
def test_create_booking_with_missing_required_fields(api_session, base_url):
    """
    GIVEN a payload missing required fields (firstname, lastname)
    WHEN POST /booking is called
    THEN the API should not crash with a 500 error

    Note: Restful-Booker is lenient and may still return 200 for incomplete
    payloads — this test documents actual behaviour, a real product API
    would likely return 400. Worth flagging as a product question in notes.
    """
    incomplete_payload = {
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-07-01",
            "checkout": "2026-07-05"
        }
    }

    response = api_session.post(f"{base_url}/booking", json=incomplete_payload)

    assert response.status_code != 500, (
        f"API crashed with 500 on missing required fields. Body: {response.text}"
    )


@pytest.mark.regression
@pytest.mark.api
def test_create_booking_with_negative_price(api_session, base_url,
                                              sample_booking_payload):
    """
    GIVEN a payload with a negative totalprice
    WHEN POST /booking is called
    THEN the API should not crash (documents whether validation exists)
    """
    payload = sample_booking_payload.copy()
    payload["totalprice"] = -50

    response = api_session.post(f"{base_url}/booking", json=payload)

    assert response.status_code != 500, (
        f"API crashed with 500 on negative price. Body: {response.text}"
    )
    # Note: if this returns 200, it's a product question worth raising —
    # negative prices probably should be rejected by the API.
