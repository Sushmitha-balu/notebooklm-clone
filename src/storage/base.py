from abc import ABC, abstractmethod
from typing import Any

CATEGORIES = ("raw", "extracted", "chats", "artifacts")


class StorageBackend(ABC):
    """Abstract storage interface. Swap LocalStorage for S3/GCS later
    without touching ingestion, retrieval, or UI code."""

    @abstractmethod
    def create_notebook(self, notebook_id: str) -> None: ...

    @abstractmethod
    def delete_notebook(self, notebook_id: str) -> None: ...

    @abstractmethod
    def list_notebooks(self) -> list[str]: ...

    @abstractmethod
    def notebook_exists(self, notebook_id: str) -> bool: ...

    @abstractmethod
    def save_file(self, notebook_id: str, category: str, filename: str, data: bytes) -> str: ...

    @abstractmethod
    def read_file(self, notebook_id: str, category: str, filename: str) -> bytes: ...

    @abstractmethod
    def list_files(self, notebook_id: str, category: str) -> list[str]: ...

    @abstractmethod
    def delete_file(self, notebook_id: str, category: str, filename: str) -> None: ...

    @abstractmethod
    def save_json(self, notebook_id: str, category: str, filename: str, obj: Any) -> None: ...

    @abstractmethod
    def load_json(self, notebook_id: str, category: str, filename: str, default: Any = None) -> Any: ...

    @abstractmethod
    def get_vector_path(self, notebook_id: str) -> str:
        """Directory where this notebook's ChromaDB persists."""

    @abstractmethod
    def save_meta(self, notebook_id: str, meta: dict) -> None: ...

    @abstractmethod
    def load_meta(self, notebook_id: str) -> dict: ...