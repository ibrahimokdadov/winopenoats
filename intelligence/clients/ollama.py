import httpx
from intelligence.clients.base import BaseLLMClient, BaseEmbeddingClient, LLMUnavailableError


class OllamaClient(BaseLLMClient, BaseEmbeddingClient):
    def __init__(self, base_url: str, llm_model: str, embedding_model: str):
        self._base = base_url.rstrip("/")
        self._llm = llm_model
        self._emb = embedding_model

    async def complete(self, messages: list[dict], stream: bool = False) -> str:
        payload = {"model": self._llm, "messages": messages, "stream": False}
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(f"{self._base}/api/chat", json=payload)
            except httpx.ConnectError:
                raise LLMUnavailableError(f"Ollama not running at {self._base}")
            if not (200 <= resp.status_code < 300):
                raise LLMUnavailableError(f"Ollama HTTP {resp.status_code}")
            return resp.json()["message"]["content"]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        results = []
        async with httpx.AsyncClient(timeout=30) as client:
            for text in texts:
                resp = await client.post(
                    f"{self._base}/api/embeddings",
                    json={"model": self._emb, "prompt": text},
                )
                results.append(resp.json()["embedding"])
        return results
