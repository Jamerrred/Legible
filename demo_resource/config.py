"""Shared settings for the resource and the constants loaded from the business's facts."""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

from mf_core.business import load_facts

SLUG = "cormorant"
STREAM = "resource"
BASE_URL = os.environ.get("MF_RESOURCE_BASE_URL", "http://agents.cormorant.localhost:8103")
SLOT_DAYS = 21
QUOTE_VALID_DAYS = 7  # This site's own limit. The facts don't set a quote validity period.

DATA = load_facts(SLUG)
BIZ = DATA["business"]
NAME = BIZ["name"]
FACTS = DATA["facts"]
FACT = {fact["id"]: fact for fact in FACTS}
MODEL = DATA["pricing_model"]
RULES = DATA["availability_rules"]
TZ = ZoneInfo(RULES["timezone"])
SIZES = list(MODEL["sizes"])
SERVICES = MODEL["services"]
ADDONS = MODEL["addons"]
CONDITIONS = MODEL["conditions"]
ZONES = MODEL["travel"]["zones"]
FEES = MODEL["timing_fees"]
TAX_RATE = MODEL["tax"]["rate"]
NEEDS_SIZE = "vehicle size class, or the make and model"
DEAD_STATUSES = ("not_offered", "out_of_area", "invalid_combination")
