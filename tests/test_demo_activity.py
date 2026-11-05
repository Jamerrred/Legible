"""The demo's sample week has to hold up when someone reads it closely."""

from __future__ import annotations

from datetime import UTC, date, datetime

from legible import demo

TODAY = date(2026, 11, 5)
VISITS = demo.sample_visits(TODAY)
QUOTED = [visit[2].get("service", "").lower() for visit in VISITS if visit[1] == "/quote"]
BOOKINGS = [visit[2] for visit in VISITS if visit[1] == "/request"]


def test_written_insights_match_the_visits():
    assert sum("ceramic" in service for service in QUOTED) == 3
    assert sum("rv" in service or "motorhome" in service for service in QUOTED) == 2


def test_bookings_fall_on_days_the_business_works():
    assert len(BOOKINGS) == 4
    for booking in BOOKINGS:
        day = date.fromisoformat(booking["when"])
        assert day > TODAY
        assert day.weekday() not in (0, 6), booking["name"]  # Closed on Sundays and Mondays.


def test_sample_contact_details_are_clearly_fake():
    for booking in BOOKINGS:
        assert booking["email"].endswith("@example.com")
        assert "-555-01" in booking["phone"]


def test_replies_go_to_real_sample_bookings():
    assert set(demo.SAMPLE_REPLIES) <= {booking["name"] for booking in BOOKINGS}


def test_sample_times_run_in_order_and_end_now():
    now = datetime(2026, 11, 5, 12, tzinfo=UTC)
    times = demo.sample_times(len(VISITS), now)
    assert times == sorted(times)
    assert times[-1] == now.isoformat(timespec="seconds")
