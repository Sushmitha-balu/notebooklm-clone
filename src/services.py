from src.generation.artifacts import ArtifactService
from src.generation.chat import ChatService
from src.generation.llm import LLMClient
from src.ingestion.loaders import IngestionError
from src.ingestion.pipeline import IngestionService
from src.notebooks.manager import NotebookManager
from src.retrieval.retrievers import DenseRetriever, HybridRetriever
from src.retrieval.vector_store import VectorStore
from src.storage.local import LocalStorage


class AppServices:
    """Wires every module together. The UI talks only to this class."""

    def __init__(self, root: str = "data/notebooks"):
        self.storage = LocalStorage(root)
        self.manager = NotebookManager(self.storage)
        self.ingestion = IngestionService(self.storage, self.manager)
        self.store = VectorStore(self.storage)
        self.retrievers = {
            "dense": DenseRetriever(self.store),
            "hybrid": HybridRetriever(self.store),
        }
        self._llm = None
        self._chat = None
        self._artifacts = None

    # LLM-backed services are created lazily so the app can start and
    # show a friendly error if the API key is missing.
    @property
    def llm(self) -> LLMClient:
        if self._llm is None:
            self._llm = LLMClient()
        return self._llm

    @property
    def chat(self) -> ChatService:
        if self._chat is None:
            self._chat = ChatService(self.storage, self.retrievers, self.llm)
        return self._chat

    @property
    def artifacts(self) -> ArtifactService:
        if self._artifacts is None:
            self._artifacts = ArtifactService(self.storage, self.store, self.llm)
        return self._artifacts

    # ---------- sources: ingest + index in one step ----------
    def _already_added(self, notebook_id: str, name: str | None = None, url: str | None = None) -> bool:
        for s in self.manager.get(notebook_id).sources:
            if url and s.get("url") == url.strip():
                return True
            if name and s["type"] != "url" and s["name"] == name:
                return True
        return False

    def add_file(self, notebook_id: str, filename: str, data: bytes) -> dict:
        if self._already_added(notebook_id, name=filename):
            raise IngestionError(f"'{filename}' is already in this notebook. Remove it first to re-upload.")
        source, chunks = self.ingestion.ingest_file(notebook_id, filename, data)
        return self._index(notebook_id, source, chunks)

    def add_url(self, notebook_id: str, url: str) -> dict:
        if self._already_added(notebook_id, url=url):
            raise IngestionError("That URL is already in this notebook. Remove it first to re-add.")
        source, chunks = self.ingestion.ingest_url(notebook_id, url)
        return self._index(notebook_id, source, chunks)

    def _index(self, notebook_id: str, source: dict, chunks: list[dict]) -> dict:
        try:
            self.store.add_chunks(notebook_id, chunks)
        except Exception:
            self.remove_source(notebook_id, source["id"])   # roll back a half-added source
            raise
        return source

    def remove_source(self, notebook_id: str, source_id: str) -> None:
        try:
            self.store.delete_source(notebook_id, source_id)
        except Exception:
            pass
        self.manager.remove_source(notebook_id, source_id)
        for category in ("raw", "extracted"):
            for name in self.storage.list_files(notebook_id, category):
                if name.startswith(source_id):
                    self.storage.delete_file(notebook_id, category, name)

    def delete_notebook(self, notebook_id: str) -> None:
        self.store.forget(notebook_id)
        self.manager.delete(notebook_id)