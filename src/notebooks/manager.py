import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.storage.base import StorageBackend


@dataclass
class Notebook:
    id: str
    name: str
    created_at: str
    sources: list[dict] = field(default_factory=list)


class NotebookManager:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def create(self, name: str) -> Notebook:
        name = (name or "").strip()
        if not name:
            raise ValueError("Notebook name cannot be empty.")
        nb = Notebook(
            id=uuid.uuid4().hex[:8],
            name=name,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.storage.create_notebook(nb.id)
        self._save(nb)
        return nb

    def get(self, notebook_id: str) -> Notebook:
        if not self.storage.notebook_exists(notebook_id):
            raise KeyError(f"Notebook '{notebook_id}' not found.")
        meta = self.storage.load_meta(notebook_id)
        return Notebook(
            id=notebook_id,
            name=meta.get("name", notebook_id),
            created_at=meta.get("created_at", ""),
            sources=meta.get("sources", []),
        )

    def list(self) -> list[Notebook]:
        return [self.get(nid) for nid in self.storage.list_notebooks()]

    def rename(self, notebook_id: str, new_name: str) -> Notebook:
        nb = self.get(notebook_id)
        nb.name = new_name.strip() or nb.name
        self._save(nb)
        return nb

    def delete(self, notebook_id: str) -> None:
        self.storage.delete_notebook(notebook_id)

    # ---- source registry (used by ingestion) ----
    def add_source(self, notebook_id: str, source: dict) -> None:
        nb = self.get(notebook_id)
        nb.sources.append(source)
        self._save(nb)

    def remove_source(self, notebook_id: str, source_id: str) -> None:
        nb = self.get(notebook_id)
        nb.sources = [s for s in nb.sources if s["id"] != source_id]
        self._save(nb)

    def _save(self, nb: Notebook) -> None:
        self.storage.save_meta(nb.id, {
            "name": nb.name,
            "created_at": nb.created_at,
            "sources": nb.sources,
        })