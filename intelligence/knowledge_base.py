import asyncio
import hashlib
import json
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Awaitable

SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass
class KBResult:
    text: str
    source_file: str
    header_context: str
    relevance_score: float


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) > max_chars and current:
            chunks.append(current.strip())
            current = s + ". "
        else:
            current += s + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text[:max_chars]]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


class KnowledgeBase:
    def __init__(self, folder: Path, embed_fn: Callable[[list[str]], Awaitable[list[list[float]]]]):
        self._folder = folder
        self._embed = embed_fn
        self._cache_dir = folder / ".openoats_cache"
        self._chunks: list[dict] = []
        self._embeddings: np.ndarray | None = None

    async def index(self, progress_cb=None) -> None:
        """Index the knowledge base folder. Blocking I/O is offloaded to a thread."""
        self._cache_dir.mkdir(exist_ok=True)
        manifest_path = self._cache_dir / "manifest.json"
        emb_path = self._cache_dir / "embeddings.npy"

        def _load_cache():
            existing = {}
            cached_emb_by_hash: dict[str, list[float]] = {}
            if manifest_path.exists() and emb_path.exists():
                try:
                    stored_embs = np.load(str(emb_path))
                    idx = 0
                    for entry in json.loads(manifest_path.read_text()):
                        for chunk_entry in entry["chunks"]:
                            h = chunk_entry.get("hash", "")
                            if idx < len(stored_embs):
                                cached_emb_by_hash[h] = stored_embs[idx].tolist()
                            idx += 1
                        existing[entry["file"]] = entry
                except Exception:
                    pass
            return existing, cached_emb_by_hash

        existing, cached_emb_by_hash = await asyncio.to_thread(_load_cache)

        files = await asyncio.to_thread(
            lambda: [f for f in self._folder.rglob("*") if f.suffix in SUPPORTED_EXTENSIONS]
        )
        new_manifest, all_chunks = [], []

        for i, f in enumerate(files):
            if progress_cb:
                progress_cb(i + 1, len(files))
            mtime = str(f.stat().st_mtime)
            key = str(f)
            text = await asyncio.to_thread(f.read_text, errors="ignore")
            header = ""
            chunks = chunk_text(text)
            chunk_hashes = [hashlib.md5(c.encode()).hexdigest() for c in chunks]

            if key in existing and existing[key]["mtime"] == mtime:
                embeddings = [cached_emb_by_hash.get(h, None) for h in chunk_hashes]
                if None in embeddings:
                    embeddings = await self._embed(chunks)
            else:
                embeddings = await self._embed(chunks)

            file_chunks = []
            for chunk, emb, h in zip(chunks, embeddings, chunk_hashes):
                chunk_entry = {"text": chunk, "file": f.name, "header": header,
                               "hash": h, "embedding": emb}
                all_chunks.append(chunk_entry)
                file_chunks.append({"text": chunk, "file": f.name, "header": header, "hash": h})
            new_manifest.append({"file": key, "mtime": mtime, "chunks": file_chunks})

        self._chunks = all_chunks
        if all_chunks:
            embs = [c["embedding"] for c in all_chunks]
            self._embeddings = np.array(embs, dtype=np.float32)
            await asyncio.to_thread(np.save, str(emb_path), self._embeddings)
        await asyncio.to_thread(
            manifest_path.write_text, json.dumps(new_manifest, indent=2)
        )

    async def search(self, query: str, top_k: int = 5) -> list[KBResult]:
        if self._embeddings is None or len(self._chunks) == 0:
            return []
        q_emb_list = await self._embed([query])
        q_emb = np.array(q_emb_list[0], dtype=np.float32)
        scores = np.array([
            cosine_similarity(q_emb, np.array(c.get("embedding", q_emb)))
            for c in self._chunks
        ])
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            KBResult(
                text=self._chunks[i]["text"],
                source_file=self._chunks[i].get("file", ""),
                header_context=self._chunks[i].get("header", ""),
                relevance_score=float(scores[i]),
            )
            for i in top_indices
        ]
