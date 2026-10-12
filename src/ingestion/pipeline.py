import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.notebooks.manager import NotebookManager
from src.storage.base import StorageBackend

from .chunking import chunk_segments
from .loaders import IngestionError, fetch_url, load_file, parse_html


class IngestionService:
    def __init__(self, storage: StorageBackend, manager: NotebookManager,
                 chunk_size: int = 1000, overlap: int = 150):
        self.storage = storage
        self.manager = manager
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _check_notebook(self, notebook_id: str):
        try:
            self.manager.get(notebook_id)
        except KeyError:
            raise IngestionError("Please select or create a notebook first.")

    def ingest_file(self, notebook_id: str, filename: str, data: bytes):
        self._check_notebook(notebook_id)
        segments = load_file(filename, data)
        ext = Path(filename).suffix.lower().lstrip(".")
        return self._finish(notebook_id, filename, ext, data, segments, url=None)

    def ingest_url(self, notebook_id: str, url: str):
        self._check_notebook(notebook_id)
        html = fetch_url(url)
        segments, title = parse_html(html)
        return self._finish(notebook_id, title or url, "url", html, segments, url=url.strip())

    def _finish(self, notebook_id, name, kind, raw_bytes, segments, url):
        source_id = uuid.uuid4().hex[:8]
        chunks = chunk_segments(segments, source_id, name, self.chunk_size, self.overlap)

        raw_name = f"{source_id}_page.html" if kind == "url" else f"{source_id}_{name}"
        self.storage.save_file(notebook_id, "raw", raw_name, raw_bytes)
        self.storage.save_json(notebook_id, "extracted", f"{source_id}.json", {
            "source_id": source_id,
            "name": name,
            "type": kind,
            "url": url,
            "segments": [asdict(s) for s in segments],
        })
        self.storage.save_json(notebook_id, "extracted", f"{source_id}.chunks.json", chunks)

        source = {
            "id": source_id,
            "name": name,
            "type": kind,
            "url": url,
            "num_chunks": len(chunks),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self.manager.add_source(notebook_id, source)
        return source, chunks