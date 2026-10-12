from src.storage.local import LocalStorage
from src.notebooks.manager import NotebookManager
from src.ingestion.pipeline import IngestionService
from src.retrieval.vector_store import VectorStore
from src.retrieval.retrievers import DenseRetriever, HybridRetriever
from src.generation.llm import LLMClient
from src.generation.chat import ChatService

storage = LocalStorage("data/notebooks")
mgr = NotebookManager(storage)
svc = IngestionService(storage, mgr)
store = VectorStore(storage)

nb = mgr.create("Chat Test")
source, chunks = svc.ingest_url(nb.id, "https://en.wikipedia.org/wiki/Retrieval-augmented_generation")
store.add_chunks(nb.id, chunks)

chat = ChatService(
    storage,
    {"dense": DenseRetriever(store), "hybrid": HybridRetriever(store)},
    LLMClient(),
)

for q in ["How does RAG reduce hallucinations?", "What are its limitations?"]:
    out = chat.ask(nb.id, q, method="hybrid")
    print("Q:", q)
    print("A:", out["answer"])
    print(f"   retrieval {out['retrieval_ms']:.0f} ms | llm {out['llm_ms']:.0f} ms")
    for s in out["sources"]:
        mark = "CITED" if s["cited"] else "     "
        print(f"   [{s['number']}] {mark} {s['source_name'][:40]} | {s['text'][:60]!r}")
    print()

print("History saved:", len(chat.get_history(nb.id)), "turns")
mgr.delete(nb.id)