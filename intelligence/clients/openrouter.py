import json
import httpx
from intelligence.clients.base import BaseLLMClient, LLMUnavailableError, LLMRateLimitError

BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterClient(BaseLLMClient):
    def __init__(self, api_key: str, base_url: str = BASE_URL, model: str = "openai/gpt-4o-mini"):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model

    def _headers(self):
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def complete(self, messages: list[dict], stream: bool = False) -> str:
        """Non-streaming completion."""
        payload = {"model": self._model, "messages": messages, "stream": False}
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                )
            except httpx.ConnectError as e:
                raise LLMUnavailableError(str(e))
            except httpx.TimeoutException as e:
                raise LLMUnavailableError(str(e))
            if resp.status_code == 429:
                raise LLMRateLimitError("Rate limit reached")
            if not (200 <= resp.status_code < 300):
                raise LLMUnavailableError(f"HTTP {resp.status_code}")
            return resp.json()["choices"][0]["message"]["content"]

    async def stream_complete(self, messages: list[dict]):
        """Streaming SSE completion — yields text chunks."""
        payload = {"model": self._model, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                ) as resp:
                    if resp.status_code == 429:
                        raise LLMRateLimitError("Rate limit reached")
                    if not (200 <= resp.status_code < 300):
                        raise LLMUnavailableError(f"HTTP {resp.status_code}")
                    async for line in resp.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            try:
                                chunk = json.loads(line[6:])
                                text = chunk["choices"][0].get("delta", {}).get("content", "")
                                if text:
                                    yield text
                            except (json.JSONDecodeError, KeyError):
                                pass
            except httpx.ConnectError as e:
                raise LLMUnavailableError(str(e))
