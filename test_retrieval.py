from src.storage.local import LocalStorage
from src.notebooks.manager import NotebookManager
from src.ingestion.pipeline import IngestionService
from src.retrieval.vector_store import VectorStore
from src.retrieval.retrievers import DenseRetriever, HybridRetriever

storage = LocalStorage("data/notebooks")
mgr = NotebookManager(storage)
svc = IngestionService(storage, mgr)
store = VectorStore(storage)

nb = mgr.create("Retrieval Test")
source, chunks = svc.ingest_url(nb.id, "https://en.wikipedia.org/wiki/Retrieval-augmented_generation")
store.add_chunks(nb.id, chunks)
print(f"Indexed {store.count(nb.id)} chunks\n")

dense, hybrid = DenseRetriever(store), HybridRetriever(store)

questions = [
    "What is retrieval-augmented generation?",
    "How does RAG reduce hallucinations?",
    "What are the limitations of RAG?",
]

for q in questions:
    print("=" * 70)
    print("Q:", q)
    for r in (dense, hybrid):
        res = r.retrieve(nb.id, q, k=3)
        print(f"\n  [{res.method}] {res.elapsed_ms:.1f} ms")
        for c in res.chunks:
            print(f"    {c['score']:.3f} | {c['id']} | {c['text'][:90]!r}")

mgr.delete(nb.id)