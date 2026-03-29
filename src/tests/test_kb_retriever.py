from src.kb_retriever import PDFKnowledgeBase


def build_kb() -> PDFKnowledgeBase:
    kb = PDFKnowledgeBase(path="data/statutes", search_mode="keyword", max_chunk_tokens=60, chunk_overlap_ratio=0.2)
    kb.chunks = [
        {
            "chunk_id": "doc:1:1",
            "text": "Tenant rights include notice before eviction and fair treatment.",
            "document_name": "TenancyAct.pdf",
            "document_path": "data/statutes/TenancyAct.pdf",
            "page_number": 1,
            "section_heading": "Section 4 Tenant Rights",
        },
        {
            "chunk_id": "doc:2:1",
            "text": "Inheritance disputes often require probate proceedings.",
            "document_name": "ProbateAct.pdf",
            "document_path": "data/statutes/ProbateAct.pdf",
            "page_number": 2,
            "section_heading": "Chapter 2",
        },
    ]
    return kb


def test_chunk_page_respects_overlap_and_size():
    kb = PDFKnowledgeBase(max_chunk_tokens=20, chunk_overlap_ratio=0.2)
    text = "\n\n".join([
        "SECTION 1 TENANT RIGHTS",
        "Tenants should receive notice before eviction.",
        "Landlords must provide safe premises.",
        "Courts may grant relief in unfair eviction cases.",
    ])

    chunks = kb.chunk_page(text)
    assert chunks
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk["text"].strip()
        assert kb.estimate_tokens(chunk["text"]) <= 28


def test_keyword_search_returns_metadata_and_scores():
    kb = build_kb()
    results = kb.search("tenant eviction rights", top_n=2)

    assert results
    top = results[0]
    assert top["search_method"] == "keyword"
    assert "document_name" in top
    assert "page_number" in top
    assert top["score"] > 0


def test_hybrid_falls_back_to_keyword_when_semantic_fails(monkeypatch):
    kb = build_kb()
    kb.search_mode = "hybrid"

    def fail_semantic(*args, **kwargs):
        raise RuntimeError("semantic unavailable")

    monkeypatch.setattr(kb, "search_semantic", fail_semantic)
    results = kb.search("tenant rights", top_n=1)

    assert len(results) == 1
    assert results[0]["search_method"] == "keyword"


def test_hybrid_prefers_semantic_when_score_is_strong(monkeypatch):
    kb = build_kb()
    kb.search_mode = "hybrid"
    kb.semantic_score_threshold = 0.2

    def strong_semantic(*args, **kwargs):
        return [
            {
                "chunk_id": "doc:1:1",
                "text": "semantic tenant result",
                "document_name": "TenancyAct.pdf",
                "document_path": "data/statutes/TenancyAct.pdf",
                "page_number": 1,
                "section_heading": "Section 4",
                "score": 0.91,
                "search_method": "semantic",
            }
        ]

    monkeypatch.setattr(kb, "search_semantic", strong_semantic)
    results = kb.search("tenant rights", top_n=1)

    assert len(results) == 1
    assert results[0]["search_method"] == "semantic"
