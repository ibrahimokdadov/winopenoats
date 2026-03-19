from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMUnavailableError(Exception):
    pass


class LLMRateLimitError(Exception):
    pass


class BaseLLMClient(ABC):
    @abstractmethod
    async def complete(
        self, messages: list[dict], stream: bool = False
    ) -> str:
        ...


class BaseEmbeddingClient(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...
