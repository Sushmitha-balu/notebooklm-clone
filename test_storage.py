from src.storage.local import LocalStorage
from src.notebooks.manager import NotebookManager

mgr = NotebookManager(LocalStorage("data/notebooks"))
nb = mgr.create("Test Notebook")
print("Created:", nb)

mgr.storage.save_file(nb.id, "raw", "../../notes test.txt", b"hello")
print("Files:", mgr.storage.list_files(nb.id, "raw"))   # safe name, no traversal

mgr.rename(nb.id, "Renamed")
print("All:", [n.name for n in mgr.list()])

mgr.delete(nb.id)
print("After delete:", len(mgr.list()))