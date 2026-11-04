"""Walk the site's whole booking flow. Usage: uv run python scripts/check_booking.py http://cormorant.localhost:8101"""

from __future__ import annotations

import sys

import httpx
from bs4 import BeautifulSoup

LEAD = {"name": "Booking Check", "email": "booking-check@example.com", "phone": "415-555-0100", "address": "1 Example St, San Francisco"}
THANKS = "Thanks! We'll be in touch soon."


def check(client: httpx.Client) -> str | None:
    """Return what went wrong, or None if the flow works from lead form to thanks page."""
    step1 = client.get("/book")
    if step1.status_code != 200:
        return f"GET /book returned {step1.status_code}"
    form = BeautifulSoup(step1.text, "html.parser").find("form")
    if form is None or not all(form.find(attrs={"name": key}) for key in LEAD):
        return "step 1 form is missing a lead field"
    incomplete = client.post("/book", data={**LEAD, "phone": ""})
    if incomplete.status_code != 422:
        return f"incomplete lead returned {incomplete.status_code}, not 422"
    step2 = client.post("/book", data=LEAD)
    if step2.status_code != 200:
        return f"POST /book returned {step2.status_code}"
    soup = BeautifulSoup(step2.text, "html.parser")
    slots = [i["value"] for i in soup.find_all("input", attrs={"name": "slot"}) if not i.has_attr("disabled")]
    if not slots:
        return "step 2 shows no open slot"
    packages = [o["value"] for o in soup.select("select[name=package] option") if o.get("value")]
    addons = [i["value"] for i in soup.find_all("input", attrs={"name": "addons"})]
    if not packages or not addons:
        return "step 2 has no packages or add-ons"
    hidden = {i["name"]: i["value"] for i in soup.find_all("input", attrs={"type": "hidden"})}
    if hidden != LEAD:
        return "step 2 didn't carry the lead fields"
    done = client.post(
        "/book/request",
        data={**LEAD, "package": packages[0], "vehicle": "2019 Honda Civic", "addons": addons[:1], "notes": "booking check", "slot": slots[0]},
    )
    if done.status_code != 200:
        return f"POST /book/request returned {done.status_code}"
    if THANKS not in BeautifulSoup(done.text, "html.parser").get_text():
        return "thanks text not found"
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check_booking.py BASE_URL")
    with httpx.Client(base_url=sys.argv[1].rstrip("/"), timeout=15) as http:
        problem = check(http)
    print("PASS" if problem is None else f"FAIL: {problem}")
    sys.exit(0 if problem is None else 1)
