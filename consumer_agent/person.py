"""The person the agent acts for: what it knows about them, their answers, and the
personal-details gate."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import unquote_plus

from .runlog import RunLog

PRIVATE_FIELDS = ("name", "email", "phone", "address")
_APPROVAL = re.compile(
    r"\b(approve|approval|permission|allow|authori[sz]e|may i|can i|shall i|should i|ok to|okay to|"
    r"is it ok|is it okay|fine to|fine if|go ahead|want me to|like me to|confirm)\b",
    re.I,
)
_OPEN_QUESTION = re.compile(r"^\s*(what|which|when|where|who|how)\b", re.I)  # "What date should I book?"
_EXPLICIT = re.compile(r"approv|permission", re.I)
_YES = re.compile(r"^\s*(yes|approve|go ahead|ok|submit|confirm|proceed)", re.I)
_NO = re.compile(r"^\s*(no|don't|do not|decline|cancel|not now)", re.I)


class Person:
    def __init__(self, spec: dict[str, Any] | None, log: RunLog):
        spec = spec or {}
        self.profile: dict[str, Any] = spec.get("profile") or {}
        self.shareable = set(spec.get("shareable_without_asking") or [])
        self.answers: dict[str, Any] = spec.get("answers") or {}
        self.approved = False
        self.log = log
        self._patterns = {
            f: self._pattern(f, str(self.profile[f]))
            for f in PRIVATE_FIELDS
            if self.profile.get(f) and f not in self.shareable
        }

    @staticmethod
    def _pattern(field: str, value: str) -> re.Pattern[str]:
        if field == "phone":
            digits = re.sub(r"\D", "", value)
            digits = digits[1:] if len(digits) == 11 and digits[0] == "1" else digits
            return re.compile(r"\D{0,3}".join(digits))
        if field == "address":  # Street number and first street word, so "St"/"Street" both hit.
            street = value.split(",")[0].strip()
            words = street.split()
            if len(words) >= 2:
                return re.compile(rf"\b{re.escape(words[0])}\s+{re.escape(words[1])}\b", re.I)
            return re.compile(re.escape(street), re.I)
        if field == "name":
            return re.compile(r"\s+".join(re.escape(w) for w in value.split()), re.I)
        return re.compile(re.escape(value), re.I)

    def memory(self) -> str:
        """What goes in the system prompt, like memory."""
        if not self.profile:
            return "Nothing on file."
        open_lines, private_lines = [], []
        for key, value in self.profile.items():
            line = f"- {key}: {value}"
            (private_lines if key in self._patterns else open_lines).append(line)
        out = []
        if open_lines:
            out.append("Fine to use when a step needs it:\n" + "\n".join(open_lines))
        if private_lines:
            out.append(
                "Private. Don't put these in any search, page address, form or brief "
                "until the person has approved it with ask_person:\n" + "\n".join(private_lines)
            )
        return "\n".join(out)

    def scan(self, args: Any) -> list[str]:
        """Names of the private fields found in a tool's arguments."""
        text = json.dumps(args, ensure_ascii=False, default=str)
        text = text + "\n" + unquote_plus(text)
        return [f for f, p in self._patterns.items() if p.search(text)]

    def redact(self, text: str) -> tuple[str, set[str]]:
        """Swap private values for browser placeholders. Returns the text and fields used."""
        used = set()
        for f, p in self._patterns.items():
            text, n = p.subn(f"<secret>person_{f}</secret>", text)
            if n:
                used.add(f)
        return text, used

    def sensitive_data(self, fields: set[str]) -> dict[str, str]:
        return {f"person_{f}": str(self.profile[f]) for f in fields if f in self._patterns}

    def private_fields(self) -> set[str]:
        return set(self._patterns)

    def answer(self, question: str, options: list[str] | None = None) -> str:
        options = options or []
        asks_approval = bool(_APPROVAL.search(question) or any(_YES.match(o) for o in options))
        if _OPEN_QUESTION.match(question) and not _EXPLICIT.search(question):
            asks_approval = False
        free_text = str(self.answers.get("free_text") or "")
        approved = False
        if asks_approval and "approve_submit" in self.answers:
            if self.answers["approve_submit"]:
                self.approved = approved = True
                pick = next((o for o in options if _YES.match(o)), "")
                text = f"Yes, approved. Go ahead.{' (' + pick + ')' if pick else ''}"
            else:
                pick = next((o for o in options if _NO.match(o)), "")
                text = f"No, I don't approve that.{' (' + pick + ')' if pick else ''}"
            if free_text:
                text += " " + free_text
        else:
            text = free_text or "I don't have anything to add. Use your best judgement."
        self.log.event(
            "approval", question=question, options=options, answer=text,
            asked_for_approval=asks_approval, approved=approved,
        )
        return text
