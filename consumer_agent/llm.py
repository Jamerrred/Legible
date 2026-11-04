"""OpenRouter chat/completions client: tools, model resolution, usage tracking, retries."""

from __future__ import annotations

import asyncio
import os
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://openrouter.ai/api/v1"
TRANSIENT_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}
_SPARK = re.compile(r"^meta/muse-spark-(\d+)\.(\d+)$")


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env")


class LLMError(RuntimeError):
    """Carries a status code and the provider's message. Never holds request headers."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def pick_model(tier: str, model_ids: list[str]) -> str:
    """spark = highest meta/muse-spark-<major>.<minor>; wonder = meta/muse-wonder."""
    if tier == "wonder":
        if "meta/muse-wonder" not in model_ids:
            raise LLMError("meta/muse-wonder is not listed by OpenRouter")
        return "meta/muse-wonder"
    if tier == "spark":
        versions = [(int(m[1]), int(m[2]), i) for i in model_ids if (m := _SPARK.match(i))]
        if not versions:
            raise LLMError("no meta/muse-spark-<major>.<minor> model is listed by OpenRouter")
        return max(versions)[2]
    if "/" in tier:  # An explicit model id.
        return tier
    raise LLMError(f"unknown tier {tier!r}")


@dataclass
class Usage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0

    def add(self, u: dict[str, Any] | None) -> None:
        self.calls += 1
        if not u:
            return
        self.prompt_tokens += u.get("prompt_tokens") or 0
        self.completion_tokens += u.get("completion_tokens") or 0
        self.total_tokens += u.get("total_tokens") or 0
        self.reasoning_tokens += (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
        self.cost += float(u.get("cost") or 0.0)

    def snapshot(self) -> dict[str, Any]:
        d = asdict(self)
        d["cost"] = round(self.cost, 6)
        return d


class LLM:
    def __init__(
        self,
        tier: str = "spark",
        reasoning_effort: str | None = "low",
        max_tokens: int = 6000,
        timeout_s: float = 120.0,
        max_retries: int = 5,
    ):
        load_env()
        self._key = os.environ.get("OPENROUTER_API_KEY", "")
        if not self._key:
            raise LLMError("OPENROUTER_API_KEY is not set")
        self.tier = tier
        self.reasoning_effort = reasoning_effort
        self.max_tokens = max(max_tokens, 4000)  # Reasoning tokens count against this.
        self.max_retries = max_retries
        self.usage = Usage()
        self.model = ""
        self._client = httpx.AsyncClient(timeout=timeout_s)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def resolve(self) -> str:
        data = await self._request("GET", "/models")
        self.model = pick_model(self.tier, [m["id"] for m in data.get("data", [])])
        return self.model

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: Any = None,
        response_format: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Returns the first choice. Reasoning can use up the limit, so a reply cut off with
        nothing to show is retried once with double the room."""
        limit = max_tokens or self.max_tokens
        for attempt in range(2):
            body: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": limit,
                "usage": {"include": True},
            }
            if self.reasoning_effort:
                body["reasoning"] = {"effort": self.reasoning_effort}
            if tools:
                body["tools"] = tools
                body["parallel_tool_calls"] = True
            if tool_choice:
                body["tool_choice"] = tool_choice
            if response_format:
                body["response_format"] = response_format
            data = await self._request("POST", "/chat/completions", body)
            self.usage.add(data.get("usage"))
            choice = data["choices"][0]
            msg = choice.get("message") or {}
            empty = not msg.get("content") and not msg.get("tool_calls")
            if not (empty and choice.get("finish_reason") == "length") or attempt == 1:
                return choice
            limit = min(limit * 2, 32000)
        return choice

    async def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._key}"}
        last: LLMError | None = None
        for attempt in range(self.max_retries):
            if attempt:
                await asyncio.sleep(min(30, 1.5 * 2 ** (attempt - 1)) + random.random())
            try:
                r = await self._client.request(method, BASE_URL + path, headers=headers, json=body)
            except httpx.TransportError as e:
                last = LLMError(f"connection problem: {type(e).__name__}")
                continue
            if r.status_code in TRANSIENT_STATUS:
                last = LLMError(f"status {r.status_code}", r.status_code)
                continue
            try:
                data = r.json()
            except ValueError:
                last = LLMError(f"status {r.status_code}: response was not JSON", r.status_code)
                continue
            err = data.get("error") if isinstance(data, dict) else None
            if r.status_code >= 400 or err:
                code = (err or {}).get("code") if isinstance(err, dict) else None
                message = str((err or {}).get("message", "") if isinstance(err, dict) else err)[:400]
                last = LLMError(f"status {code or r.status_code}: {message}", code or r.status_code)
                if "provider returned error" in str(message).lower():
                    continue
                if code in TRANSIENT_STATUS:  # OpenRouter can put an upstream failure in a 200.
                    continue
                raise last
            if path.endswith("completions") and not data.get("choices"):
                last = LLMError("response had no choices")
                continue
            return data
        raise last or LLMError("request failed")
