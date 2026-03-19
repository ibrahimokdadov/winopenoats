import json
import numpy as np
import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from intelligence.knowledge_base import KnowledgeBase, chunk_text, cosine_similarity


def test_chunk_text_basic():
    chunks = chunk_text("Hello world. " * 100, max_chars=200)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 250


def test_cosine_similarity():
    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    assert cosine_similarity(a, b) == pytest.approx(1.0)
    c = np.array([0.0, 1.0])
    assert cosine_similarity(a, c) == pytest.approx(0.0)


async def test_search_returns_results(tmp_path):
    (tmp_path / "notes.md").write_text("# Sales\nWe sell widgets at $10 each.")
    mock_embed = AsyncMock(return_value=[[0.1, 0.9]])
    kb = KnowledgeBase(folder=tmp_path, embed_fn=mock_embed)
    await kb.index()
    results = await kb.search("widget price", top_k=3)
    assert isinstance(results, list)


async def test_cache_created(tmp_path):
    (tmp_path / "doc.md").write_text("Content here.")
    mock_embed = AsyncMock(return_value=[[0.5, 0.5]])
    kb = KnowledgeBase(folder=tmp_path, embed_fn=mock_embed)
    await kb.index()
    cache_dir = tmp_path / ".openoats_cache"
    assert (cache_dir / "embeddings.npy").exists()
    assert (cache_dir / "manifest.json").exists()
