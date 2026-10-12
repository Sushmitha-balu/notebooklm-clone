import shutil
from pathlib import Path

from src.storage.local import LocalStorage
from src.notebooks.manager import NotebookManager
from src.ingestion.pipeline import IngestionService
from src.retrieval.vector_store import VectorStore
from src.generation.llm import LLMClient
from src.generation.artifacts import ArtifactService

storage = LocalStorage("data/notebooks")
mgr = NotebookManager(storage)
svc = IngestionService(storage, mgr)
store = VectorStore(storage)

nb = mgr.create("RAG Basics")
source, chunks = svc.ingest_url(nb.id, "https://en.wikipedia.org/wiki/Retrieval-augmented_generation")
store.add_chunks(nb.id, chunks)

art = ArtifactService(storage, store, LLMClient())

report = art.generate_report(nb.id, nb.name)
print(report["markdown"][:800], "\n...\n")

quiz = art.generate_quiz(nb.id, nb.name, num_questions=5)
print(quiz["quiz_markdown"][:600], "\n...\n")
print(quiz["key_markdown"][:400], "\n...\n")

print("Saved:", art.list_artifacts(nb.id))

# Copy the files out so you can open them before the notebook is deleted
out = Path("artifact_test_output")
out.mkdir(exist_ok=True)
for name in art.list_artifacts(nb.id):
    (out / name).write_bytes(art.read_artifact(nb.id, name))
print("Copied to", out.resolve())

mgr.delete(nb.id)