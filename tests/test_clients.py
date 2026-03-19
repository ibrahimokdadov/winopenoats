import pytest
import httpx
import respx
from intelligence.clients.base import LLMRateLimitError
from intelligence.clients.openrouter import OpenRouterClient
from intelligence.clients.ollama import OllamaClient
from intelligence.clients.voyage import VoyageClient

MESSAGES = [{"role": "user", "content": "hello"}]


@respx.mock
async def test_openrouter_complete():
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={
            "choices": [{"message": {"content": "hi there"}}]
        })
    )
    client = OpenRouterClient(api_key="test-key")
    result = await client.complete(MESSAGES)
    assert result == "hi there"


@respx.mock
async def test_openrouter_429_raises():
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=httpx.Response(429)
    )
    client = OpenRouterClient(api_key="test-key")
    with pytest.raises(LLMRateLimitError):
        await client.complete(MESSAGES)


@respx.mock
async def test_ollama_embed():
    respx.post("http://localhost:11434/api/embeddings").mock(
        return_value=httpx.Response(200, json={"embedding": [0.1, 0.2, 0.3]})
    )
    client = OllamaClient(
        base_url="http://localhost:11434",
        llm_model="llama3",
        embedding_model="nomic",
    )
    result = await client.embed(["hello"])
    assert result == [[0.1, 0.2, 0.3]]


@respx.mock
async def test_voyage_embed():
    respx.post("https://api.voyageai.com/v1/embeddings").mock(
        return_value=httpx.Response(200, json={"data": [{"embedding": [0.5, 0.6]}]})
    )
    client = VoyageClient(api_key="test-key")
    result = await client.embed(["hello"])
    assert result == [[0.5, 0.6]]


@respx.mock
async def test_voyage_rerank():
    respx.post("https://api.voyageai.com/v1/rerank").mock(
        return_value=httpx.Response(200, json={
            "data": [
                {"index": 0, "relevance_score": 0.9},
                {"index": 1, "relevance_score": 0.4},
            ]
        })
    )
    client = VoyageClient(api_key="test-key")
    scores = await client.rerank("query", ["doc a", "doc b"])
    assert len(scores) == 2
    assert scores[0] == pytest.approx(0.9)
