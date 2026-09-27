from pathlib import Path
from typing import Any

import chromadb

from backend.config import get_settings

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"
COLLECTION_NAME = "smart_trip_travel_knowledge"


def split_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    normalized = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(normalized[start:end])
        start = max(end - overlap, start + 1)
    return chunks


def _collection() -> Any:
    client = chromadb.PersistentClient(path=get_settings().chroma_path)
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def ingest_documents(force: bool = False) -> int:
    collection = _collection()
    if force and collection.count():
        collection.delete(where={"source": {"$ne": ""}})
    if collection.count():
        return collection.count()
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    for path in sorted(DOCUMENTS_DIR.glob("*.md")):
        for index, chunk in enumerate(split_text(path.read_text(encoding="utf-8"))):
            ids.append(f"{path.stem}-{index}")
            documents.append(chunk)
            metadatas.append({"source": path.name, "chunk": index})
    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(documents)


def retrieve(query: str, limit: int = 5) -> list[dict[str, str]]:
    collection = _collection()
    if collection.count() == 0:
        ingest_documents()
    result = collection.query(query_texts=[query], n_results=min(limit, collection.count()))
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    return [
        {"text": text, "source": metadata.get("source", "unknown")}
        for text, metadata in zip(documents, metadatas)
    ]
