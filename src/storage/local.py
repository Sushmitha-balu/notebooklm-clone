import json
import re
import shutil
from pathlib import Path
from typing import Any

from .base import CATEGORIES, StorageBackend

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(name: str) -> str:
    """Strip directories and unsafe characters (prevents path traversal)."""
    name = Path(name).name
    name = _SAFE_NAME.sub("_", name).strip("._")
    return name or "unnamed"


class LocalStorage(StorageBackend):
    def __init__(self, root: str = "data/notebooks"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    # ---------- path helpers ----------
    def _nb(self, notebook_id: str) -> Path:
        notebook_id = safe_filename(notebook_id)
        path = (self.root / notebook_id).resolve()
        if self.root not in path.parents:
            raise ValueError("Invalid notebook id")
        return path

    def _cat(self, notebook_id: str, category: str) -> Path:
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        return self._nb(notebook_id) / category

    # ---------- notebooks ----------
    def create_notebook(self, notebook_id: str) -> None:
        base = self._nb(notebook_id)
        for cat in CATEGORIES:
            (base / cat).mkdir(parents=True, exist_ok=True)
        (base / "chroma").mkdir(exist_ok=True)

    def delete_notebook(self, notebook_id: str) -> None:
        shutil.rmtree(self._nb(notebook_id), ignore_errors=True)

    def list_notebooks(self) -> list[str]:
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def notebook_exists(self, notebook_id: str) -> bool:
        return self._nb(notebook_id).is_dir()

    # ---------- files ----------
    def save_file(self, notebook_id, category, filename, data: bytes) -> str:
        path = self._cat(notebook_id, category) / safe_filename(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path.name

    def read_file(self, notebook_id, category, filename) -> bytes:
        return (self._cat(notebook_id, category) / safe_filename(filename)).read_bytes()

    def list_files(self, notebook_id, category) -> list[str]:
        d = self._cat(notebook_id, category)
        return sorted(p.name for p in d.iterdir() if p.is_file()) if d.exists() else []

    def delete_file(self, notebook_id, category, filename) -> None:
        (self._cat(notebook_id, category) / safe_filename(filename)).unlink(missing_ok=True)

    # ---------- json ----------
    def save_json(self, notebook_id, category, filename, obj: Any) -> None:
        data = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self.save_file(notebook_id, category, filename, data)

    def load_json(self, notebook_id, category, filename, default: Any = None) -> Any:
        try:
            return json.loads(self.read_file(notebook_id, category, filename))
        except FileNotFoundError:
            return default

    # ---------- notebook metadata ----------
    def save_meta(self, notebook_id: str, meta: dict) -> None:
     path = self._nb(notebook_id) / "meta.json"
     path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
               
    def load_meta(self, notebook_id: str) -> dict:
     path = self._nb(notebook_id) / "meta.json"
     return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    # ---------- vector DB ----------
    def get_vector_path(self, notebook_id: str) -> str:
        path = self._nb(notebook_id) / "chroma"
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


 