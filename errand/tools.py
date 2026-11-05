"""The agent's tools, the search backends, and the two code gates."""

from __future__ import annotations

import ast
import asyncio
import json
import math
import operator
import os
import re
import secrets
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urldefrag, urljoin, urlparse
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

from .person import Person
from .runlog import RunLog

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0 Safari/537.36 PersonalAssistant/1.0 (software fetching a page for a person)"
)
OUTCOMES = ("answered", "not_offered", "unknown", "action_submitted", "needs_person", "blocked")
EVIDENCE = ("verified_at_source", "listed_unverified", "unknown")
IMAGE_NOTE = "This tool can't see what an image shows. Only the alt text and address are known."
GATED_TOOLS = {"search_web", "read_page", "browse_task"}

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "search_web": {
        "description": "Search the web. Pass several queries to run them together. Returns titles, URLs, excerpts and dates. Excerpts can be partial or out of date.",
        "parameters": {
            "type": "object",
            "properties": {"queries": {"type": "array", "items": {"type": "string"}, "description": "One or more search queries"}},
            "required": ["queries"],
        },
    },
    "read_page": {
        "description": "Fetch one web page with no JavaScript. Returns its text, the links on the page (text and URL), images (alt text and address only), any forms, and whether the text was cut off.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "detail": {"type": "string", "enum": ["concise", "detailed"], "description": "concise returns less text; detailed returns up to the full limit"},
                "offset": {"type": "integer", "description": "Character position to continue from, if an earlier read was cut off"},
            },
            "required": ["url"],
        },
    },
    "browse_task": {
        "description": "Hand a job to a separate live browser worker. It sees rendered pages, including images and scripts, and it can click and fill in forms. It can't see this conversation, so the brief must stand alone. Slow: use it when reading can't settle something. May only submit after the person has approved with ask_person.",
        "parameters": {
            "type": "object",
            "properties": {
                "objective": {"type": "string", "description": "One sentence"},
                "start_url": {"type": "string"},
                "details": {"type": "string", "description": "Exact dates, sizes and options"},
                "return_fields": {"type": "array", "items": {"type": "string"}, "description": "What to report back"},
                "may_submit": {"type": "boolean", "description": "False means check only"},
                "submit_details": {"type": "string", "description": "What to enter if it may submit"},
            },
            "required": ["objective", "start_url"],
        },
    },
    "do_math": {
        "description": "Exact arithmetic and date work. Give expression for arithmetic, or date_op for dates.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "For example 375 + 39 or (120 * 1.08) + 15"},
                "date_op": {"type": "string", "enum": ["today", "weekday", "add_days", "days_between"]},
                "date": {"type": "string", "description": "YYYY-MM-DD. For add_days it defaults to today"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD, for days_between"},
                "days": {"type": "integer", "description": "For add_days"},
                "timezone": {"type": "string", "description": "IANA name such as America/Chicago. Use the business's timezone"},
            },
        },
    },
    "ask_person": {
        "description": "Ask the person you act for a question, or for approval to share their details or submit something.",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}}},
            "required": ["question"],
        },
    },
    "finish": {
        "description": "Give your final report and end the job. Outcomes: answered, not_offered (the business says it doesn't offer this), unknown (couldn't settle it), action_submitted (the page confirmed it), needs_person (the person must decide or act), blocked (login, payment or a technical wall stopped you). A price, time or number in a verified_at_source claim must appear in something a tool returned.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The report to the person, grouped by evidence quality"},
                "outcome": {"type": "string", "enum": list(OUTCOMES)},
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {"type": "string"},
                            "value": {"type": "string"},
                            "source_url": {"type": "string"},
                            "evidence": {"type": "string", "enum": list(EVIDENCE)},
                        },
                        "required": ["claim", "value", "evidence"],
                    },
                },
                "mapped_terms": {"type": "array", "items": {"type": "string"}, "description": "How the customer's words map to the business's categories"},
                "next_steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["answer", "outcome", "claims"],
        },
    },
}


# ---- Search backends ----


class SearchBackend(Protocol):
    async def search(self, query: str, k: int = 8) -> list[dict[str, Any]]: ...
    async def stored_page(self, url: str) -> dict[str, Any] | None: ...


def _tokens(text: str) -> list[str]:
    out = []
    for t in re.findall(r"[a-z0-9]+(?:[.'][a-z0-9]+)*", text.lower()):
        out.append(t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t)
    return out


def _url_key(url: str) -> str:
    p = urlparse(urldefrag(url)[0])
    return f"{p.netloc.lower()}{p.path.rstrip('/')}{'?' + p.query if p.query else ''}"


class LocalCorpusBackend:
    """BM25 over a directory of saved page copies: {"url","title","text","fetched_at"}."""

    K1, B = 1.5, 0.75

    def __init__(self, corpus_dir: str | Path):
        self.docs: list[dict[str, Any]] = []
        for path in sorted(Path(corpus_dir).rglob("*.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(doc, dict) and doc.get("url") and doc.get("text"):
                self.docs.append(doc)
        self.tfs = [Counter(_tokens(d.get("title", "")) * 2 + _tokens(d["text"])) for d in self.docs]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 1.0
        self.df: Counter[str] = Counter()
        for tf in self.tfs:
            self.df.update(tf.keys())
        self.by_url = {_url_key(d["url"]): d for d in self.docs}

    def _idf(self, term: str) -> float:
        n, df = len(self.docs), self.df.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def _best_passage(self, text: str, terms: set[str], width: int = 600) -> str:
        chunks: list[str] = []
        for para in re.split(r"\n+", text):
            para = para.strip()
            while para:
                chunks.append(para[:width])
                para = para[width:]
        merged: list[str] = []
        for c in chunks:
            if merged and len(merged[-1]) + len(c) < width:
                merged[-1] += " " + c
            else:
                merged.append(c)
        if not merged:
            return ""
        return max(merged, key=lambda c: sum(self._idf(t) for t in terms & set(_tokens(c))))

    async def search(self, query: str, k: int = 8) -> list[dict[str, Any]]:
        terms = _tokens(query)
        scored = []
        for i, tf in enumerate(self.tfs):
            s = 0.0
            for t in terms:
                f = tf.get(t, 0)
                if f:
                    norm = 1 - self.B + self.B * self.lengths[i] / self.avg
                    s += self._idf(t) * f * (self.K1 + 1) / (f + self.K1 * norm)
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        return [
            {
                "title": self.docs[i].get("title", ""),
                "url": self.docs[i]["url"],
                "excerpt": self._best_passage(self.docs[i]["text"], set(terms)),
                "date": self.docs[i].get("fetched_at"),
            }
            for _, i in scored[:k]
        ]

    async def stored_page(self, url: str) -> dict[str, Any] | None:
        return self.by_url.get(_url_key(url))


class ExaBackend:
    def __init__(self) -> None:
        self._key = os.environ.get("EXA_API_KEY", "")
        if not self._key:
            raise RuntimeError("EXA_API_KEY is not set")
        self._client = httpx.AsyncClient(timeout=30, headers={"x-api-key": self._key})

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(3):
            if attempt:
                await asyncio.sleep(1.5 * attempt)
            try:
                r = await self._client.post(f"https://api.exa.ai{path}", json=body)
            except httpx.TransportError:
                continue
            if r.status_code in (429, 500, 502, 503, 504):
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError("search provider unavailable")

    async def search(self, query: str, k: int = 8) -> list[dict[str, Any]]:
        data = await self._post("/search", {
            "query": query,
            "type": "auto",
            "numResults": k,
            "contents": {"highlights": {"numSentences": 3, "highlightsPerUrl": 2}},
        })
        return [
            {
                "title": r.get("title") or "",
                "url": r.get("url"),
                "excerpt": " ... ".join(r.get("highlights") or [])[:800] or (r.get("text") or "")[:600],
                "date": r.get("publishedDate"),
            }
            for r in data.get("results", [])
        ]

    async def stored_page(self, url: str) -> dict[str, Any] | None:
        data = await self._post("/contents", {"urls": [url], "text": True})
        for r in data.get("results", []):
            if r.get("text"):
                return {"url": r.get("url") or url, "title": r.get("title") or "", "text": r["text"], "fetched_at": r.get("publishedDate")}
        return None


# ---- Page parsing ----

_BLOCKS = "address article aside blockquote dd details div dl dt fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hr li main nav ol p pre section table tr ul".split()


def _hidden(tag: Any) -> bool:
    style = (tag.get("style") or "").replace(" ", "").lower() if tag.attrs else ""
    return tag.has_attr("hidden") or "display:none" in style or "visibility:hidden" in style


def parse_html(html: str, base_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    meta = soup.find("meta", attrs={"name": "description"})
    description = (meta.get("content") or "").strip() if meta else ""
    for tag in soup(["script", "style", "template", "head"]):
        tag.decompose()
    for tag in [t for t in soup.find_all(True) if _hidden(t)]:
        tag.decompose()

    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        alt = (img.get("alt") or "").strip()
        images.append({"alt": alt, "src": "(inline data)" if src.startswith("data:") else urljoin(base_url, src)})
        img.replace_with(f"[image: {alt or 'no alt text'}]")

    links, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:")):
            continue
        url = urljoin(base_url, href)
        text = a.get_text(" ", strip=True) or a.get("aria-label") or a.get("title") or ""
        if (text, url) not in seen:
            seen.add((text, url))
            links.append({"text": text, "url": url})

    forms = []
    for f in soup.find_all("form"):
        fields = []
        for el in f.find_all(["input", "select", "textarea"]):
            kind = el.get("type", el.name)
            if kind in ("hidden", "submit", "button"):
                continue
            label = None
            if el.get("id"):
                lab = f.find("label", attrs={"for": el["id"]})
                label = lab.get_text(" ", strip=True) if lab else None
            field = {"name": el.get("name"), "type": kind, "label": label or el.get("placeholder"), "required": el.has_attr("required")}
            if el.name == "select":
                field["options"] = [o.get_text(strip=True) for o in el.find_all("option")][:30]
            fields.append(field)
        forms.append({"action": urljoin(base_url, f.get("action") or ""), "method": (f.get("method") or "get").lower(), "fields": fields})
    frames = [urljoin(base_url, fr["src"]) for fr in soup.find_all("iframe", src=True)]

    for br in soup.find_all("br"):
        br.replace_with("\n")
    for cell in soup.find_all(["td", "th"]):
        cell.insert_after(" | ")
    for el in soup.find_all(_BLOCKS):
        el.insert_before("\n")
        el.insert_after("\n")
    raw = soup.get_text("")
    lines = [re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in raw.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    return {"title": title, "description": description, "text": text, "links": links, "images": images, "forms": forms, "frames": frames}


# ---- do_math ----

_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"round": round, "min": min, "max": max, "abs": abs, "sum": lambda *a: sum(a), "ceil": math.ceil, "floor": math.floor}


def safe_eval(expression: str) -> float | int:
    def walk(n: ast.AST) -> Any:
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _BINOPS:
            left, right = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e6):
                raise ValueError("exponent too large")
            return _BINOPS[type(n.op)](left, right)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UNARY:
            return _UNARY[type(n.op)](walk(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords:
            return _FUNCS[n.func.id](*[walk(a) for a in n.args])
        raise ValueError("only numbers, + - * / // % **, and round, min, max, abs, sum, ceil, floor are allowed")

    cleaned = re.sub(r"(?<=\d),(?=\d{3}\b)", "", expression.replace("$", ""))
    value = walk(ast.parse(cleaned, mode="eval"))
    if isinstance(value, float):
        value = round(value, 10)
        if value.is_integer():
            value = int(value)
    return value


def do_math(args: dict[str, Any], now: datetime) -> dict[str, Any]:
    if args.get("expression"):
        return {"expression": args["expression"], "result": safe_eval(str(args["expression"]))}
    op = args.get("date_op")
    tz = ZoneInfo(args.get("timezone") or "UTC")
    local = now.astimezone(tz)

    def day(value: str | None) -> date:
        return date.fromisoformat(value) if value else local.date()

    if op == "today":
        return {"date": local.date().isoformat(), "weekday": local.strftime("%A"), "time": local.strftime("%H:%M"), "timezone": str(tz)}
    if op == "weekday":
        d = day(args.get("date"))
        return {"date": d.isoformat(), "weekday": d.strftime("%A")}
    if op == "add_days":
        d = day(args.get("date")) + timedelta(days=int(args.get("days", 0)))
        return {"date": d.isoformat(), "weekday": d.strftime("%A")}
    if op == "days_between":
        return {"days": (day(args.get("end_date")) - day(args.get("date"))).days}
    raise ValueError("give expression, or date_op: today, weekday, add_days or days_between")


# ---- Evidence gate ----

_NUM = re.compile(r"\d[\d,]*(?:[.:]\d+)?")


def _forms(token: str) -> set[str]:
    t = token.replace(",", "")
    if ":" in t:
        h, m = t.split(":", 1)
        hour = int(h)
        out = {f"{hour}:{m}"}
        if hour > 12:
            out.add(f"{hour - 12}:{m}")
        if m == "00":
            out |= {str(hour)} | ({str(hour - 12)} if hour > 12 else set())
        return out
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return {t.lstrip("0") or "0"}


def number_forms(text: str) -> set[str]:
    out: set[str] = set()
    for tok in _NUM.findall(text):
        out |= _forms(tok)
    return out


def check_finish(args: dict[str, Any], seen_numbers: set[str], task: str) -> tuple[list[str], list[int]]:
    """Returns (problems, indexes of offending claims)."""
    problems, bad = [], []
    if args.get("outcome") not in OUTCOMES:
        problems.append(f"outcome must be one of {', '.join(OUTCOMES)}")
    if not str(args.get("answer") or "").strip():
        problems.append("answer is empty")
    task_numbers = number_forms(task)
    for i, c in enumerate(args.get("claims") or []):
        if not isinstance(c, dict) or c.get("evidence") != "verified_at_source":
            continue
        label = str(c.get("claim") or c.get("value"))[:100]
        if not str(c.get("source_url") or "").strip():
            problems.append(f"claim {i} ({label}) is marked verified but has no source_url")
            bad.append(i)
            continue
        missing = [tok for tok in _NUM.findall(str(c.get("value") or "")) if not _forms(tok) & seen_numbers]
        missing += [tok for tok in _NUM.findall(str(c.get("claim") or "")) if not _forms(tok) & (seen_numbers | task_numbers)]
        if missing:
            problems.append(f"claim {i} ({label}): {', '.join(sorted(set(missing)))} isn't in anything a tool returned")
            bad.append(i)
    return problems, bad


# ---- The toolbox ----


class ToolBox:
    def __init__(
        self, allowed: list[str], person: Person, log: RunLog, llm: Any, cfg: Any, now: datetime, out_dir: Path,
        backend: SearchBackend | None = None, stored_only: bool = False,
    ):
        self.allowed, self.person, self.log, self.llm, self.cfg = allowed, person, log, llm, cfg
        self.now, self.out_dir, self.backend, self.stored_only = now, out_dir, backend, stored_only
        self.calls_used = 0
        self.browse_used = 0
        self.deadline = time.monotonic() + cfg.wall_clock_s
        self.seen_numbers: set[str] = set()
        self._http = httpx.AsyncClient(timeout=25, follow_redirects=True, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    async def aclose(self) -> None:
        await self._http.aclose()
        client = getattr(self.backend, "_client", None)
        if client is not None:
            await client.aclose()

    def schemas(self, only: list[str] | None = None) -> list[dict[str, Any]]:
        names = only or self.allowed
        return [{"type": "function", "function": {"name": n, **TOOL_SCHEMAS[n]}} for n in self.allowed if n in names]

    async def run_calls(self, calls: list[tuple[str, str, dict[str, Any]]]) -> dict[str, str]:
        """calls = (call_id, name, args), finish excluded. Questions to the person go first so
        any approval is on record before the rest run together."""
        out: dict[str, str] = {}
        admitted = []
        for cid, name, args in calls:
            if name not in self.allowed:
                out[cid] = _err(f"{name} isn't available. Use one of: {', '.join(self.allowed)}.")
            elif self.calls_used >= self.cfg.max_tool_calls:
                out[cid] = _err("The tool-call budget is spent. Call finish now and say what's unverified.")
            else:
                self.calls_used += 1
                admitted.append((cid, name, args))
        for cid, name, args in admitted:
            if name == "ask_person":
                out[cid] = await self._execute(name, args)
        rest = [(c, n, a) for c, n, a in admitted if n != "ask_person"]
        results = await asyncio.gather(*(self._execute(n, a) for _, n, a in rest))
        out.update({c: r for (c, _, _), r in zip(rest, results)})
        return out

    async def _execute(self, name: str, args: dict[str, Any]) -> str:
        if name in GATED_TOOLS:
            found = self.person.scan(args)
            if found and not self.person.approved:
                self.log.event("unsafe_blocked", tool=name, fields=found, reason="personal details without approval")
                self.log.event("tool_call", tool=name, args="(withheld: contained personal details)")
                msg = (
                    f"Refused: this call contains the person's {', '.join(found)}, and they haven't approved "
                    "sharing it. Remove it, or get approval with ask_person first if a booking really needs it."
                )
                self.log.event("tool_result", tool=name, chars=len(msg), truncated=False, error=True)
                return _err(msg)
        self.log.event("tool_call", tool=name, args=args)
        t0 = time.monotonic()
        try:
            result = await getattr(self, f"_tool_{name}")(args)
        except Exception as e:  # Errors go back to the model with what to do next.
            result = {"error": f"{name} failed: {type(e).__name__}: {str(e)[:300]}. Try a different approach."}
        text = json.dumps(result, ensure_ascii=False, default=str)
        if "error" not in result:
            self.seen_numbers |= number_forms(text)
        self.log.event(
            "tool_result", tool=name, chars=len(text), truncated=bool(result.get("truncated")),
            error="error" in result, seconds=round(time.monotonic() - t0, 2), result=text[:4000],
        )
        return text

    async def _tool_search_web(self, args: dict[str, Any]) -> dict[str, Any]:
        queries = args.get("queries") or []
        if isinstance(queries, str):
            queries = [queries]
        if not queries:
            return {"error": "Give at least one query."}
        if self.backend is None:
            return {"error": "Search isn't available."}

        async def one(q: str) -> dict[str, Any]:
            try:
                return {"query": q, "results": await self.backend.search(q)}
            except Exception:
                return {"query": q, "results": [], "problem": "This search failed. Try again or rephrase."}

        return {"searches": await asyncio.gather(*(one(q) for q in queries[:6]))}

    async def _tool_read_page(self, args: dict[str, Any]) -> dict[str, Any]:
        url = str(args.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            return {"error": "Give a full http or https URL."}
        detail = args.get("detail") if args.get("detail") in ("concise", "detailed") else "concise"
        offset = max(int(args.get("offset") or 0), 0)
        limit = self.cfg.max_page_chars if detail == "detailed" else min(12000, self.cfg.max_page_chars)
        link_cap = 200 if detail == "detailed" else 80

        if self.stored_only:
            doc = await self.backend.stored_page(url) if self.backend else None
            if not doc:
                return {"error": "No copy of this page is available. Try another result."}
            page = {"title": doc.get("title", ""), "description": "", "text": doc["text"], "links": [], "images": [], "forms": [], "frames": []}
            meta: dict[str, Any] = {"url": doc["url"], "copy_date": doc.get("fetched_at")}
        else:
            r = await self._http.get(url)
            kind = r.headers.get("content-type", "").split(";")[0].strip().lower()
            meta = {"url": url, "final_url": str(r.url), "status": r.status_code}
            if r.status_code >= 400:
                return {"error": f"The page returned status {r.status_code}. Don't retry it; try a link from the site or a search.", **meta}
            if "html" in kind or not kind:
                page = parse_html(r.text, str(r.url))
            elif kind.startswith("text/") or "json" in kind or "xml" in kind:
                page = {"title": "", "description": "", "text": r.text, "links": [], "images": [], "forms": [], "frames": []}
            else:
                return {**meta, "content_type": kind, "text": "", "note": f"This tool can't read {kind}. browse_task may be able to open it."}

        full = page["text"]
        text = full[offset : offset + limit]
        end = offset + len(text)
        cut = end < len(full)
        out: dict[str, Any] = {**meta, "title": page["title"]}
        if page["description"]:
            out["description"] = page["description"]
        out.update(text=text, total_chars=len(full), truncated=cut)
        if cut:
            out["how_to_read_more"] = f"Call read_page with this url, detail='detailed' and offset={end}."
        out["links"] = page["links"][:link_cap]
        if len(page["links"]) > link_cap:
            out["links_cut_off"] = f"{len(page['links']) - link_cap} more links. Use detail='detailed' to see up to 200."
        out["images"] = page["images"][:40]
        if page["images"]:
            out["images_note"] = IMAGE_NOTE
        if page["forms"]:
            out["forms"] = page["forms"]
        if page["frames"]:
            out["embedded_frames"] = page["frames"]
        return out

    async def _tool_do_math(self, args: dict[str, Any]) -> dict[str, Any]:
        return do_math(args, self.now)

    async def _tool_ask_person(self, args: dict[str, Any]) -> dict[str, Any]:
        return {"answer": self.person.answer(str(args.get("question") or ""), args.get("options"))}

    async def _tool_browse_task(self, args: dict[str, Any]) -> dict[str, Any]:
        from .worker import build_brief, run_worker  # Heavy import; only runs that browse pay for it.

        if self.browse_used >= self.cfg.max_browse_calls:
            return {"error": f"The limit of {self.cfg.max_browse_calls} browser jobs is used up. Work with what you have."}
        may_submit = bool(args.get("may_submit"))
        if may_submit and not self.person.approved:
            self.log.event("unsafe_blocked", tool="browse_task", fields=[], reason="may_submit without approval")
            return {"error": "Refused: the person hasn't approved a submission. Ask with ask_person first, or set may_submit to false."}
        remaining = self.deadline - time.monotonic()
        wall = min(self.cfg.browser_wall_clock_s, remaining - 30)
        if wall < 45:
            return {"error": "Not enough time is left for a browser job. Call finish and say what's unverified."}
        self.browse_used += 1

        fields: set[str] = set()
        objective, used = self.person.redact(str(args.get("objective") or ""))
        fields |= used
        details, used = self.person.redact(str(args.get("details") or ""))
        fields |= used
        submit_details, used = self.person.redact(str(args.get("submit_details") or ""))
        fields |= used
        if may_submit:
            for f in self.person.private_fields():  # "use my name and email" with no values given.
                if re.search(rf"\b{f}\b", submit_details, re.I):
                    fields.add(f)
        sensitive = self.person.sensitive_data(fields)
        brief = build_brief(
            objective, str(args["start_url"]), details, list(args.get("return_fields") or []),
            may_submit, submit_details, sorted(sensitive),
        )
        worker_dir = self.out_dir / "browser" / f"worker-{self.browse_used}-{secrets.token_hex(2)}"
        self.log.event("worker_start", brief=brief, start_url=args["start_url"], may_submit=may_submit, sensitive_fields=sorted(sensitive), wall_clock_s=wall)
        before = self.llm.usage.snapshot()
        out = await run_worker(
            self.llm, brief, str(args["start_url"]), worker_dir, sensitive_data=sensitive,
            max_steps=self.cfg.browser_max_steps, wall_clock_s=wall,
        )
        after = self.llm.usage.snapshot()
        report = out["report"]
        if report.get("submitted") and not may_submit:
            report["blockers"].append("The worker reports a submission although it was told to check only.")
        self.log.event(
            "worker_end", report=report, urls_visited=report.get("urls_visited"), steps=out["steps"],
            finished=out["finished"], seconds=out["seconds"], history_path=out["history_path"],
            json_mode=out["json_mode"], tokens=after["total_tokens"] - before["total_tokens"],
            cost=round(after["cost"] - before["cost"], 6),
        )
        return report


def _err(message: str) -> str:
    return json.dumps({"error": message})
