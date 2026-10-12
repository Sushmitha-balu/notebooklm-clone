import re
import time
from datetime import datetime, timezone

from src.storage.base import StorageBackend

from .llm import LLMClient

SYSTEM_PROMPT = """You are a research assistant that answers questions using ONLY the numbered source excerpts provided.

Rules:
- Ground every claim in the excerpts and cite them inline with bracketed numbers like [1] or [2][3].
- If the excerpts do not contain the answer, say you couldn't find it in the notebook's sources. Do not use outside knowledge.
- Be concise and clear. Do not invent citations."""

NO_SOURCES_MSG = "This notebook has no indexed sources yet. Upload a file or add a URL first."


def _format_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, start=1):
        m = c["metadata"]
        loc = f", {m['location']}" if m.get("location") else ""
        blocks.append(f"[{i}] (Source: {m['source_name']}{loc})\n{c['text']}")
    return "\n\n".join(blocks)


class ChatService:
    HISTORY_FILE = "history.json"

    def __init__(self, storage: StorageBackend, retrievers: dict, llm: LLMClient,
                 k: int = 5, default_method: str = "hybrid"):
        self.storage = storage
        self.retrievers = retrievers          # {"dense": DenseRetriever, "hybrid": HybridRetriever}
        self.llm = llm
        self.k = k
        self.default_method = default_method

    def ask(self, notebook_id: str, question: str, method: str | None = None,
            history_turns: int = 4) -> dict:
        question = (question or "").strip()
        if not question:
            raise ValueError("Please enter a question.")

        method = method or self.default_method
        result = self.retrievers[method].retrieve(notebook_id, question, self.k)

        if not result.chunks:
            return {"answer": NO_SOURCES_MSG, "sources": [], "method": method,
                    "retrieval_ms": result.elapsed_ms, "llm_ms": 0.0}

        # Recent turns give the model conversational context
        history = self.get_history(notebook_id)[-history_turns:]
        messages = []
        for turn in history:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        messages.append({
            "role": "user",
            "content": f"Source excerpts:\n\n{_format_context(result.chunks)}\n\nQuestion: {question}",
        })

        start = time.perf_counter()
        answer = self.llm.complete(SYSTEM_PROMPT, messages)
        llm_ms = (time.perf_counter() - start) * 1000

        cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
        sources = []
        for i, c in enumerate(result.chunks, start=1):
            m = c["metadata"]
            sources.append({
                "number": i,
                "source_name": m["source_name"],
                "location": m.get("location", ""),
                "text": c["text"],
                "score": c["score"],
                "cited": i in cited,
            })

        out = {"answer": answer, "sources": sources, "method": method,
               "retrieval_ms": result.elapsed_ms, "llm_ms": llm_ms}
        self._append_history(notebook_id, question, out)
        return out

    # ---------- history ----------
    def get_history(self, notebook_id: str) -> list[dict]:
        return self.storage.load_json(notebook_id, "chats", self.HISTORY_FILE, default=[])

    def clear_history(self, notebook_id: str) -> None:
        self.storage.save_json(notebook_id, "chats", self.HISTORY_FILE, [])

    def _append_history(self, notebook_id: str, question: str, out: dict) -> None:
        history = self.get_history(notebook_id)
        history.append({
            "question": question,
            "answer": out["answer"],
            "sources": out["sources"],
            "method": out["method"],
            "retrieval_ms": out["retrieval_ms"],
            "llm_ms": out["llm_ms"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.storage.save_json(notebook_id, "chats", self.HISTORY_FILE, history)