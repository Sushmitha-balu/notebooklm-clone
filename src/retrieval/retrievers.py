import re
import time
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from .vector_store import VectorStore


@dataclass
class RetrievalResult:
    chunks: list[dict]      # each has id, text, metadata, score
    elapsed_ms: float
    method: str


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class DenseRetriever:
    """Approach 1: embedding similarity search only."""
    name = "dense"

    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve(self, notebook_id: str, query: str, k: int = 5) -> RetrievalResult:
        start = time.perf_counter()
        chunks = self.store.query(notebook_id, query, k)
        return RetrievalResult(chunks, (time.perf_counter() - start) * 1000, self.name)


class HybridRetriever:
    """Approach 2: dense + BM25 keyword search, merged with Reciprocal Rank Fusion."""
    name = "hybrid"

    def __init__(self, store: VectorStore, rrf_k: int = 60, pool_multiplier: int = 3):
        self.store = store
        self.rrf_k = rrf_k
        self.pool_multiplier = pool_multiplier
        self._bm25_cache = {}   # notebook_id -> (chunk_count, bm25, chunks)

    def _bm25(self, notebook_id: str):
        count = self.store.count(notebook_id)
        cached = self._bm25_cache.get(notebook_id)
        if cached and cached[0] == count:
            return cached[1], cached[2]
        chunks = self.store.get_all(notebook_id)
        bm25 = BM25Okapi([_tokenize(c["text"]) for c in chunks]) if chunks else None
        self._bm25_cache[notebook_id] = (count, bm25, chunks)
        return bm25, chunks

    def retrieve(self, notebook_id: str, query: str, k: int = 5) -> RetrievalResult:
        start = time.perf_counter()
        pool = k * self.pool_multiplier

        dense = self.store.query(notebook_id, query, pool)

        bm25, all_chunks = self._bm25(notebook_id)
        keyword = []
        if bm25:
            scores = bm25.get_scores(_tokenize(query))
            top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:pool]
            keyword = [all_chunks[i] for i in top if scores[i] > 0]

        fused, by_id = {}, {}
        for ranking in (dense, keyword):
            for rank, c in enumerate(ranking, start=1):
                fused[c["id"]] = fused.get(c["id"], 0) + 1 / (self.rrf_k + rank)
                by_id[c["id"]] = c

        ordered = sorted(fused, key=fused.get, reverse=True)[:k]
        chunks = [{**by_id[i], "score": fused[i]} for i in ordered]
        return RetrievalResult(chunks, (time.perf_counter() - start) * 1000, self.name)