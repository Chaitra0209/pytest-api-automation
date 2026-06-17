"""
tests/test_bookings_data_driven.py — Day 2 (Part 2)

Demonstrates loading test data from an external JSON file instead of
hardcoding payloads inline. This is a very common real-world pattern:
testers/developers update the JSON file without touching test code.

New concepts introduced:
  - json.load() to read external test data
  - pytest.mark.parametrize fed by a loaded list (not hardcoded values)
  - Test IDs (ids=...) to make parametrized test names readable in reports
"""

import json
import os
import pytest


# ── Load test data once at module level ───────────────────────────────────────
# This runs ONE time when pytest collects this file, not once per test.

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "test_data", "booking_test_data.json")

with open(DATA_FILE, "r") as f:
    test_data = json.load(f)

VALID_BOOKINGS = test_data["valid_bookings"]
INVALID_PRICE_BOOKINGS = test_data["invalid_price_bookings"]


# ── Data-driven happy path tests ───────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.api
@pytest.mark.parametrize(
    "booking_payload",
    VALID_BOOKINGS,
    ids=[b["firstname"] + "_" + b["lastname"] for b in VALID_BOOKINGS]
)
def test_create_booking_with_various_valid_payloads(api_session, base_url, booking_payload):
    """
    GIVEN multiple valid booking payloads loaded from JSON
    WHEN POST /booking is called for each
    THEN each should succeed with 200 and matching echoed data

    This single test function runs 3 times (once per entry in the JSON file),
    and thanks to `ids=`, your test report shows readable names like:
      test_create_booking_with_various_valid_payloads[Sally_Brown]
      test_create_booking_with_various_valid_payloads[Raj_Kumar]
      test_create_booking_with_various_valid_payloads[Min_Lee]
    instead of [booking_payload0], [booking_payload1], [booking_payload2]
    """
    response = api_session.post(f"{base_url}/booking", json=booking_payload)

    assert response.status_code == 200, (
        f"Failed for {booking_payload['firstname']}: {response.text}"
    )

    body = response.json()
    returned = body["booking"]
    assert returned["firstname"] == booking_payload["firstname"]
    assert returned["lastname"] == booking_payload["lastname"]
    assert returned["totalprice"] == booking_payload["totalprice"]


# ── Data-driven edge case tests ────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.api
@pytest.mark.parametrize(
    "price_case",
    INVALID_PRICE_BOOKINGS,
    ids=[case["description"] for case in INVALID_PRICE_BOOKINGS]
)
def test_create_booking_with_edge_case_prices(api_session, base_url,
                                                sample_booking_payload, price_case):
    """
    GIVEN edge-case price values (negative, zero, extremely large) from JSON
    WHEN POST /booking is called
    THEN the API should not crash with a 500 error for any of them

    Demonstrates combining a fixture (sample_booking_payload) with
    parametrized data (price_case) — a common real pattern.
    """
    payload = sample_booking_payload.copy()
    payload["totalprice"] = price_case["totalprice"]

    response = api_session.post(f"{base_url}/booking", json=payload)

    assert response.status_code != 500, (
        f"API crashed for case '{price_case['description']}' "
        f"(price={price_case['totalprice']}). Body: {response.text}"
    )
