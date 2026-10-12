from src.storage.local import LocalStorage
from src.notebooks.manager import NotebookManager
from src.ingestion.pipeline import IngestionService
from src.ingestion.loaders import IngestionError

storage = LocalStorage("data/notebooks")
mgr = NotebookManager(storage)
svc = IngestionService(storage, mgr)
nb = mgr.create("Ingestion Test")

# 1) TXT
text = (
    "Retrieval-Augmented Generation combines a retriever with a language model.\n\n"
    "The retriever finds relevant passages from a knowledge base. "
    "The generator then writes an answer grounded in those passages.\n\n"
) * 15
source, chunks = svc.ingest_file(nb.id, "sample.txt", text.encode())
print("TXT ->", source["num_chunks"], "chunks")
print("First chunk metadata:", chunks[0]["metadata"])

# 2) URL
try:
    source, chunks = svc.ingest_url(nb.id, "https://en.wikipedia.org/wiki/Retrieval-augmented_generation")
    print("URL ->", source["name"], "|", source["num_chunks"], "chunks")
except IngestionError as e:
    print("URL failed:", e)

# 3) Bad input gives a friendly error
try:
    svc.ingest_file(nb.id, "photo.png", b"fake")
except IngestionError as e:
    print("Expected error:", e)

# Inspect what was stored
for cat in ("raw", "extracted"):
    print(cat, "->", storage.list_files(nb.id, cat))
print("Sources in meta:", [s["name"] for s in mgr.get(nb.id).sources])

# 4) PDF and PPTX test (uncomment after putting real files in this folder)
# for f in ("yourfile.pdf", "yourslides.pptx"):
#     with open(f, "rb") as fh:
#         s, c = svc.ingest_file(nb.id, f, fh.read())
#     print(f, "->", s["num_chunks"], "chunks | first location:", c[0]["metadata"]["location"])

mgr.delete(nb.id)