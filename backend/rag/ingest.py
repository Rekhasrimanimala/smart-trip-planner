from backend.rag.retriever import ingest_documents

if __name__ == "__main__":
    print(f"Indexed {ingest_documents(force=True)} travel knowledge chunks.")
