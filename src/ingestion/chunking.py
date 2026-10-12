import re

from .loaders import Segment


def _tail(text: str, overlap: int) -> str:
    """Last `overlap` chars, trimmed to a word boundary."""
    t = text[-overlap:]
    idx = t.find(" ")
    return t[idx + 1:] if idx != -1 else t


def _units(text: str, size: int):
    """Yield paragraph-sized units; fall back to sentences, then hard splits."""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if len(para) <= size:
            yield para
            continue
        for sent in re.split(r"(?<=[.!?])\s+", para):
            sent = sent.strip()
            while len(sent) > size:
                yield sent[:size]
                sent = sent[size:]
            if sent:
                yield sent


def split_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    chunks, current = [], ""
    for unit in _units(text, size):
        if current and len(current) + len(unit) + 1 > size:
            chunks.append(current)
            current = _tail(current, overlap)
        current = f"{current}\n{unit}".strip() if current else unit
    if current:
        chunks.append(current)
    return chunks


def chunk_segments(
    segments: list[Segment],
    source_id: str,
    source_name: str,
    size: int = 1000,
    overlap: int = 150,
) -> list[dict]:
    """Returns chunks shaped for ChromaDB: {id, text, metadata}."""
    chunks, n = [], 0
    for seg in segments:
        for piece in split_text(seg.text, size, overlap):
            chunks.append({
                "id": f"{source_id}-{n}",
                "text": piece,
                "metadata": {
                    "source_id": source_id,
                    "source_name": source_name,
                    "location": seg.location,
                    "page": seg.page,
                    "chunk_index": n,
                },
            })
            n += 1
    return chunks