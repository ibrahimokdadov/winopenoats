import httpx
from intelligence.clients.base import BaseEmbeddingClient, LLMUnavailableError

BASE = "https://api.voyageai.com/v1"


class VoyageClient(BaseEmbeddingClient):
    def __init__(self, api_key: str, model: str = "voyage-3-lite"):
        self._api_key = api_key
        self._model = model

    def _headers(self):
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{BASE}/embeddings",
                json={"model": self._model, "input": texts},
                headers=self._headers(),
            )
            if not (200 <= resp.status_code < 300):
                raise LLMUnavailableError(f"Voyage HTTP {resp.status_code}")
            return [item["embedding"] for item in resp.json()["data"]]

    async def rerank(self, query: str, candidates: list[str]) -> list[float]:
        """Returns a relevance score (0.0–1.0) per candidate, same order as input."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{BASE}/rerank",
                json={"model": "rerank-2", "query": query, "documents": candidates},
                headers=self._headers(),
            )
            if not (200 <= resp.status_code < 300):
                raise LLMUnavailableError(f"Voyage rerank HTTP {resp.status_code}")
            ranked = resp.json()["data"]
            scores = [0.0] * len(candidates)
            for item in ranked:
                scores[item["index"]] = item["relevance_score"]
            return scores
