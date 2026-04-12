import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import fitz

from .logger import log_error
from .vector_store import ChromaVectorStore


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    document_name: str
    document_path: str
    page_number: int
    section_heading: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "document_name": self.document_name,
            "document_path": self.document_path,
            "page_number": self.page_number,
            "section_heading": self.section_heading,
        }


class PDFKnowledgeBase:
    def __init__(
        self,
        path: Optional[str] = None,
        search_mode: str = "hybrid",
        semantic_score_threshold: float = 0.2,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        vector_store_dir: str = "storage/vector_store",
        collection_name: str = "statutes",
        max_chunk_tokens: int = 800,
        chunk_overlap_ratio: float = 0.15,
    ):
        self.path = path or "corpus/raw"
        self.search_mode = search_mode
        self.semantic_score_threshold = semantic_score_threshold
        self.embedding_model_name = embedding_model_name
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_overlap_ratio = chunk_overlap_ratio

        self.chunks: List[Dict[str, Any]] = []
        self._bm25 = None
        self._embedder = None
        self._semantic_index_ready = False
        self._vector_store = ChromaVectorStore(
            persist_directory=vector_store_dir, collection_name=collection_name
        )

    @staticmethod
    def estimate_tokens(text: str) -> int:
        # Lightweight approximation that avoids tokenizer dependencies.
        return max(1, len(text) // 4)

    @staticmethod
    def _infer_heading(paragraph: str) -> Optional[str]:
        first_line = paragraph.strip().splitlines()[0] if paragraph.strip() else ""
        if not first_line:
            return None

        heading_patterns = [
            r"^[A-Z][A-Z\s\-,:]{4,}$",
            r"^\d+(\.\d+)*\s+[A-Za-z].*",
            r"^(Section|Part|Chapter)\s+\w+",
        ]
        for pattern in heading_patterns:
            if re.match(pattern, first_line.strip()):
                return first_line.strip()
        return None

    def chunk_page(self, text: str) -> List[Dict[str, Any]]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if not paragraphs:
            return []

        overlap_tokens = max(1, int(self.max_chunk_tokens * self.chunk_overlap_ratio))
        result: List[Dict[str, Any]] = []

        current: List[str] = []
        current_tokens = 0
        current_heading: Optional[str] = None

        for paragraph in paragraphs:
            paragraph_tokens = self.estimate_tokens(paragraph)
            inferred_heading = self._infer_heading(paragraph)
            if inferred_heading and current_heading is None:
                current_heading = inferred_heading

            if current and (current_tokens + paragraph_tokens > self.max_chunk_tokens):
                chunk_text = "\n\n".join(current).strip()
                result.append({"text": chunk_text, "section_heading": current_heading})

                # Carry token overlap from the tail into next chunk.
                tail: List[str] = []
                tail_tokens = 0
                for prev in reversed(current):
                    prev_tokens = self.estimate_tokens(prev)
                    if tail_tokens + prev_tokens > overlap_tokens:
                        break
                    tail.insert(0, prev)
                    tail_tokens += prev_tokens

                current = tail.copy()
                current_tokens = tail_tokens
                current_heading = self._infer_heading(current[0]) if current else None

            current.append(paragraph)
            current_tokens += paragraph_tokens

            if inferred_heading:
                current_heading = inferred_heading

        if current:
            chunk_text = "\n\n".join(current).strip()
            result.append({"text": chunk_text, "section_heading": current_heading})

        return result

    def load_pdf(self):
        self.chunks = []
        self._bm25 = None
        self._semantic_index_ready = False

        if not os.path.isdir(self.path):
            raise FileNotFoundError(f"Knowledge base path does not exist: {self.path}")

        pdf_files = sorted(name for name in os.listdir(self.path) if name.lower().endswith(".pdf"))
        if not pdf_files:
            return

        for filename in pdf_files:
            full_path = os.path.join(self.path, filename)
            doc = fitz.open(full_path)
            for page_idx, page in enumerate(doc, start=1):
                page_text = page.get_text() or ""
                for local_idx, piece in enumerate(self.chunk_page(page_text), start=1):
                    if not piece["text"]:
                        continue
                    chunk_id = f"{filename}:{page_idx}:{local_idx}"
                    self.chunks.append(
                        ChunkRecord(
                            chunk_id=chunk_id,
                            text=piece["text"],
                            document_name=filename,
                            document_path=full_path,
                            page_number=page_idx,
                            section_heading=piece.get("section_heading"),
                        ).to_dict()
                    )

    def _get_embedder(self):
        if self._embedder is not None:
            return self._embedder

        try:
            from sentence_transformers import SentenceTransformer
        except Exception as exc:
            raise RuntimeError(
                "sentence-transformers is required for semantic retrieval"
            ) from exc

        self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = self._get_embedder()
        vectors = model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    def _build_semantic_index(self) -> None:
        if self._semantic_index_ready or not self.chunks:
            return

        texts = [chunk["text"] for chunk in self.chunks]
        vectors = self._embed_texts(texts)
        ids = [chunk["chunk_id"] for chunk in self.chunks]
        metadatas = [
            {
                "chunk_id": chunk["chunk_id"],
                "document_name": chunk["document_name"],
                "document_path": chunk["document_path"],
                "page_number": chunk["page_number"],
                "section_heading": chunk.get("section_heading") or "",
            }
            for chunk in self.chunks
        ]
        self._vector_store.clear()
        self._vector_store.upsert(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
        self._semantic_index_ready = True

    # Common English stopwords that pollute keyword scoring in legal texts
    _STOPWORDS = frozenset(
        "a an the is was were be been being am are and or but if of in to for on "
        "with at by from it its this that these those not no nor so as do does did "
        "has have had may will shall can could would should i me my we our you your "
        "he she they them their his her who what which when where how all any each "
        "than too very also about after before between into through during under "
        "above below up down out off over again further then once here there".split()
    )

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and filter stopwords for BM25 indexing."""
        return [w for w in re.split(r"\W+", text.lower()) if w and w not in self._STOPWORDS]

    def _build_bm25_index(self) -> None:
        """Build the BM25 index from loaded chunks (lazy, called on first keyword search)."""
        if self._bm25 is not None or not self.chunks:
            return
        from rank_bm25 import BM25Okapi
        tokenized_corpus = [self._tokenize(chunk["text"]) for chunk in self.chunks]
        self._bm25 = BM25Okapi(tokenized_corpus)

    def _search_keyword_fallback(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """Simple word-frequency fallback for tiny corpora where BM25 IDF degenerates."""
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []
        results: List[Dict[str, Any]] = []
        for chunk in self.chunks:
            chunk_lower = chunk["text"].lower()
            score = sum(chunk_lower.count(w) for w in query_tokens)
            if score > 0:
                enriched = dict(chunk)
                enriched["score"] = float(score)
                enriched["search_method"] = "keyword"
                results.append(enriched)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

    def search_keyword(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        self._build_bm25_index()
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)

        # Get top-n indices by score
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]

        results: List[Dict[str, Any]] = []
        for idx in ranked_indices:
            if scores[idx] <= 0:
                continue
            enriched = dict(self.chunks[idx])
            enriched["score"] = float(scores[idx])
            enriched["search_method"] = "keyword"
            results.append(enriched)

        # BM25 IDF degenerates with very small corpora (< 10 docs) — fall back
        if not results:
            return self._search_keyword_fallback(query, top_n)

        return results

    def search_semantic(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        if not query or not self.chunks:
            return []

        self._build_semantic_index()
        query_vector = self._embed_texts([query])[0]
        candidates = self._vector_store.query(query_vector, top_n=top_n)

        results: List[Dict[str, Any]] = []
        for candidate in candidates:
            text = candidate.get("document") or ""
            metadata = candidate.get("metadata") or {}
            results.append(
                {
                    "chunk_id": metadata.get("chunk_id"),
                    "text": text,
                    "document_name": metadata.get("document_name", ""),
                    "document_path": metadata.get("document_path", ""),
                    "page_number": metadata.get("page_number", 0),
                    "section_heading": metadata.get("section_heading") or None,
                    "score": float(candidate.get("score", 0.0)),
                    "search_method": "semantic",
                }
            )
        return results

    def search(self, query, top_n=3):
        """
        Unified retrieval interface with backward-compatible signature.
        Returns metadata-rich chunks while still including `text` and `score`.
        """
        if not query:
            return []

        mode = (self.search_mode or "hybrid").lower()

        if mode == "keyword":
            return self.search_keyword(query, top_n=top_n)

        if mode == "semantic":
            try:
                return self.search_semantic(query, top_n=top_n)
            except Exception as exc:
                log_error(f"Semantic search failed ({exc}); falling back to keyword mode")
                return self.search_keyword(query, top_n=top_n)

        # Hybrid mode — Reciprocal Rank Fusion (RRF)
        keyword_results = self.search_keyword(query, top_n=top_n * 2)
        semantic_results: List[Dict[str, Any]] = []
        try:
            semantic_results = self.search_semantic(query, top_n=top_n * 2)
        except Exception as exc:
            log_error(f"Hybrid semantic path failed ({exc}); falling back to keyword mode")
            return keyword_results[:top_n]

        return self._rrf_merge(keyword_results, semantic_results, top_n=top_n)

    @staticmethod
    def _rrf_merge(
        keyword_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]],
        top_n: int = 3,
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion: score(d) = sum(1 / (k + rank_i))"""
        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(keyword_results, start=1):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            doc_map[cid] = item

        for rank, item in enumerate(semantic_results, start=1):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            if cid not in doc_map:
                doc_map[cid] = item

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results: List[Dict[str, Any]] = []
        for cid, fused_score in ranked[:top_n]:
            entry = dict(doc_map[cid])
            entry["score"] = fused_score
            entry["search_method"] = "hybrid_rrf"
            results.append(entry)
        return results


if __name__ == "__main__":
    kb = PDFKnowledgeBase(path="corpus/raw")
    kb.load_pdf()
    results = kb.search("tenant rights", top_n=3)
    if not results:
        print("No matching chunks found.")
    else:
        for i, result in enumerate(results, 1):
            print(
                f"\nResult {i} [{result.get('search_method', 'unknown')}] "
                f"(Score: {result['score']:.3f})"
            )
            print(f"Source: {result.get('document_name')} p.{result.get('page_number')}")
            print(result["text"][:240] + "...")
            print("-" * 40)

