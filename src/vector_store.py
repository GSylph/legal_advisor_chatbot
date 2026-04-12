from typing import Any, Dict, List, Optional


class ChromaVectorStore:
    """Minimal Chroma wrapper to isolate optional dependency handling."""

    def __init__(self, persist_directory: str, collection_name: str) -> None:
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._collection = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection

        try:
            import chromadb
        except Exception as exc:
            raise RuntimeError("chromadb is required for semantic retrieval") from exc

        client = chromadb.PersistentClient(path=self.persist_directory)
        self._collection = client.get_or_create_collection(name=self.collection_name)
        return self._collection

    def clear(self) -> None:
        collection = self._get_collection()
        existing = collection.get(include=[])
        ids = existing.get("ids", []) if existing else []
        if ids:
            collection.delete(ids=ids)

    def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 5000,
    ) -> None:
        if not ids:
            return
        collection = self._get_collection()
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            collection.upsert(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

    def query(self, query_embedding: List[float], top_n: int = 3) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        response = collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1, top_n),
            include=["distances", "metadatas", "documents"],
        )

        docs = (response.get("documents") or [[]])[0]
        metas = (response.get("metadatas") or [[]])[0]
        distances = (response.get("distances") or [[]])[0]

        results: List[Dict[str, Any]] = []
        for idx, doc in enumerate(docs):
            metadata: Optional[Dict[str, Any]] = metas[idx] if idx < len(metas) else {}
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            score = 1.0 / (1.0 + max(distance, 0.0))
            results.append(
                {
                    "document": doc,
                    "metadata": metadata or {},
                    "score": score,
                }
            )
        return results
