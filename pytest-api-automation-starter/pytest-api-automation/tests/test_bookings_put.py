"""
tests/test_bookings_put.py — Day 3 (Part 1)

Tests for PUT /booking/{id} (full update) and PATCH /booking/{id} (partial update).

New concepts introduced:
  - Stacked @parametrize decorators (creates a multiplication of test cases)
  - Using auth_token fixture for authenticated requests
  - pytest.mark.skip and pytest.mark.skipif
"""

import pytest


# ── PUT — full update (requires auth) ──────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
def test_update_booking_with_valid_data_succeeds(api_session, base_url,
                                                    created_booking, auth_token):
    """
    GIVEN an existing booking and valid auth token
    WHEN PUT /booking/{id} is called with new data
    THEN the booking is fully updated and response reflects new values
    """
    booking_id = created_booking

    updated_payload = {
        "firstname": "UpdatedFirst",
        "lastname": "UpdatedLast",
        "totalprice": 500,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-10-01",
            "checkout": "2026-10-05"
        },
        "additionalneeds": "Late checkout"
    }

    response = api_session.put(
        f"{base_url}/booking/{booking_id}",
        json=updated_payload,
        headers={"Cookie": f"token={auth_token}"}
    )

    assert response.status_code == 200, f"PUT failed: {response.text}"
    body = response.json()
    assert body["firstname"] == "UpdatedFirst"
    assert body["totalprice"] == 500


@pytest.mark.regression
@pytest.mark.api
def test_update_booking_without_auth_token_is_rejected(api_session, base_url,
                                                          created_booking):
    """
    GIVEN an existing booking but NO auth token
    WHEN PUT /booking/{id} is called
    THEN the request should be rejected (401 or 403), not silently succeed

    This is a security-relevant negative test — checking that the API
    enforces authentication rather than allowing anonymous writes.
    """
    booking_id = created_booking

    updated_payload = {
        "firstname": "ShouldNotWork",
        "lastname": "NoAuth",
        "totalprice": 999,
        "depositpaid": False,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        "additionalneeds": ""
    }

    # Deliberately no Cookie/auth header
    response = api_session.put(f"{base_url}/booking/{booking_id}", json=updated_payload)

    assert response.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {response.status_code}. "
        f"This may indicate the API does not enforce authentication on PUT."
    )


# ── PATCH — partial update ───────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.api
# Stacked parametrize: this creates 2 x 2 = 4 test combinations automatically
@pytest.mark.parametrize("field", ["firstname", "totalprice"])
@pytest.mark.parametrize("auth_valid", [True, False])
def test_patch_booking_field_combinations(api_session, base_url, created_booking,
                                            auth_token, field, auth_valid):
    """
    GIVEN a combination of (field to update) x (valid or invalid auth)
    WHEN PATCH /booking/{id} is called
    THEN behaviour should be consistent: success only with valid auth

    Stacked @parametrize multiplies combinations:
      2 fields × 2 auth states = 4 total test runs:
        [True-firstname]   [True-totalprice]
        [False-firstname]  [False-totalprice]

    This is useful when you want to test every combination of two
    independent variables without writing 4 separate test functions.
    """
    booking_id = created_booking

    new_value = "PatchedName" if field == "firstname" else 777
    patch_payload = {field: new_value}

    headers = {"Cookie": f"token={auth_token}"} if auth_valid else {"Cookie": "token=invalid_token_123"}

    response = api_session.patch(
        f"{base_url}/booking/{booking_id}",
        json=patch_payload,
        headers=headers
    )

    if auth_valid:
        assert response.status_code == 200, (
            f"PATCH with valid auth should succeed for field '{field}'. "
            f"Got {response.status_code}: {response.text}"
        )
    else:
        assert response.status_code in (401, 403), (
            f"PATCH with invalid auth should be rejected for field '{field}'. "
            f"Got {response.status_code}: {response.text}"
        )


# ── skip / skipif demonstration ──────────────────────────────────────────────

@pytest.mark.skip(reason="Restful-Booker does not support bulk PATCH - documenting as not testable on this API")
def test_patch_multiple_bookings_in_bulk():
    """
    Placeholder test showing how to mark something as skipped rather than
    deleting it — keeps the test plan visible even if not runnable yet.
    """
    pass


@pytest.mark.skipif(
    True,  # In a real project, this would be a condition like: os.environ.get("ENV") == "prod"
    reason="Example skipif - would normally check environment, e.g. skip destructive tests in prod"
)
def test_example_skipif_pattern():
    """
    Demonstrates skipif syntax for conditional skipping based on environment,
    feature flags, or other runtime conditions. Hardcoded True here only
    to demonstrate the syntax pattern.
    """
    pass
