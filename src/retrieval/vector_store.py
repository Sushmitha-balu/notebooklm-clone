import chromadb

from src.storage.base import StorageBackend

from .embeddings import embed_texts


class VectorStore:
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self._clients = {}

    def _collection(self, notebook_id: str):
        if notebook_id not in self._clients:
            path = self.storage.get_vector_path(notebook_id)
            self._clients[notebook_id] = chromadb.PersistentClient(path=path)
        return self._clients[notebook_id].get_or_create_collection(
            name="chunks", metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, notebook_id: str, chunks: list[dict], batch: int = 64) -> None:
        col = self._collection(notebook_id)
        for i in range(0, len(chunks), batch):
            part = chunks[i:i + batch]
            texts = [c["text"] for c in part]
            col.add(
                ids=[c["id"] for c in part],
                documents=texts,
                embeddings=embed_texts(texts),
                metadatas=[c["metadata"] for c in part],
            )

    def query(self, notebook_id: str, query: str, k: int = 5) -> list[dict]:
        col = self._collection(notebook_id)
        n = col.count()
        if n == 0:
            return []
        res = col.query(
            query_embeddings=embed_texts([query]),
            n_results=min(k, n),
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"id": i, "text": d, "metadata": m, "score": 1 - dist}  # cosine similarity
            for i, d, m, dist in zip(
                res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
            )
        ]

    def get_all(self, notebook_id: str) -> list[dict]:
        """All chunks (used to build the BM25 keyword index)."""
        col = self._collection(notebook_id)
        if col.count() == 0:
            return []
        res = col.get(include=["documents", "metadatas"])
        return [
            {"id": i, "text": d, "metadata": m}
            for i, d, m in zip(res["ids"], res["documents"], res["metadatas"])
        ]

    def delete_source(self, notebook_id: str, source_id: str) -> None:
        self._collection(notebook_id).delete(where={"source_id": source_id})

    def count(self, notebook_id: str) -> int:
        return self._collection(notebook_id).count()

    def forget(self, notebook_id: str) -> None:
        self._clients.pop(notebook_id, None)