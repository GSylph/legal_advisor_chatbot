# Retrieval Benchmark — Methodology & Reproducibility

> Generated: 2026-03-31
> Script: `eval/retrieval_benchmark.py`
> Output: `eval/retrieval_results.json`
> Reproduce: `uv run python eval/retrieval_benchmark.py`

---

## 1. What We Measured

For each of 200 benchmark questions (`data/benchmark.json`), we retrieved the top-k chunks (k=3 and k=5) using three retriever modes and checked whether the retrieved chunks come from the **correct statute and section**.

### Metrics

| Metric | Definition | Intuition |
|--------|-----------|-----------|
| **Precision@k** | `relevant_in_top_k / k` | Of the k chunks returned, what fraction are from the right statute+section? |
| **Recall@k (Hit Rate)** | `1 if any relevant chunk in top_k, else 0` | Did the retriever find *at least one* correct chunk? Binary because gold labels are abstract (one label per question, not per chunk). |
| **Hit@k** | Same as Recall@k here | Equivalent in our setup since each question has one gold statute reference. |

### Why binary recall?

Our gold labels specify a statute+section (e.g., "Employment Act 1968, Section 11") but not specific chunk IDs from our corpus. Multiple chunks may contain the relevant section text. A chunk-level recall denominator would require exhaustive relevance annotation of all 8,604 chunks, which is infeasible. Binary recall ("did we find at least one relevant chunk?") is standard practice when gold labels are at the document/passage level rather than chunk level.

---

## 2. How Gold Matching Works

### The Problem (v1 → v2)

**v1 (rejected):** Check if the gold citation string (e.g., "Employment Act 1968, Section 11") appears literally in the retrieved chunk's body text.

**v1 results:** P@3 ≈ 0.07, Hit@3 ≈ 0.13 — artificially low.

**Why v1 failed:** PDF-extracted statute text rarely contains the act's own name. A chunk from Section 11 of the Employment Act reads:

```
11.—(1) Either party to a contract of service may at any time
give to the other party notice of his intention to terminate…
```

The string "Employment Act 1968" does not appear — it's only on the title page or running headers, which typically fall in different chunks.

### Approaches Considered

| # | Approach | Verdict | Reason |
|---|----------|---------|--------|
| 1 | Full-text citation match | **Too strict** | Act name missing from body text → mass false negatives |
| 2 | Document filename only | **Too lenient** | Any chunk from the right PDF counts, even wrong sections |
| 3 | Filename + raw section integer | **False positives** | Small numbers (4, 7) match page numbers, dates, cross-refs |
| 4 | Filename + strict statute pattern | **Misses continuations** | Mid-section chunks lack the "11.—(1)" header |
| 5 | Semantic similarity (gold answer ↔ chunk) | **Circular** | Tests retrieval using the same embedding model; also slow |
| 6 | Filename + relaxed section detection | **Selected** | Best precision/recall balance, reproducible, explainable |

### v2 Matching Rules (Selected)

A retrieved chunk is scored as **relevant** if:

1. **Document match:** The chunk's `document_name` field (e.g., `employment_act_1968.pdf`) maps to the gold statute's act name (e.g., "Employment Act 1968"). The mapping normalizes both to lowercase with underscores/spaces removed.

2. **Section match (if applicable):** The gold statute's section number (e.g., "11") is found in either:
   - The chunk's **text**, via statute-format regex patterns:
     - `11.—` or `11.-` (Singapore statute numbering)
     - `Section 11` or `section 11`
     - `s.11` or `s 11`
     - `§11` or `§ 11`
   - The chunk's **`section_heading`** metadata field (same patterns)

3. **No section specified:** If the gold statute has no section number (e.g., "Personal Data Protection Act 2012"), document match alone is sufficient.

4. **No corpus PDF:** If the gold statute references a source without a corresponding corpus PDF (e.g., "Common law", "EU GDPR", "PDPC Advisory Guidelines"), the question is **excluded** from scoring and reported as `n_excluded`.

### Filename Resolution

The function `resolve_act_to_filename()` maps gold act names to corpus PDFs:

```
"Employment Act 1968"                    → employment_act_1968.pdf         (direct)
"Personal Data Protection Act 2012"      → personal_data_protection_act_2012.pdf (direct)
"Employment Act 1968 (Amendment 2019)"   → employment_act_1968.pdf         (strip amendment)
"Consumer Protection (Fair Trading) Act" → (token subset match)            (fuzzy)
"Common law (wrongful dismissal)"        → None (excluded)
```

Resolution order: exact normalized match → strip amendment/cap suffix → token-subset match (≥60% overlap). If no match, the question is excluded.

---

## 3. Retriever Implementations

| Mode | Implementation | Scoring |
|------|---------------|---------|
| **BM25** | `kb_retriever.search_keyword()` — `rank_bm25.BM25Okapi` with stopword-filtered tokenization. TF-IDF with document length normalization (k1=1.5, b=0.75). Falls back to word-frequency scoring for very small corpora (<10 docs) where BM25 IDF degenerates. | BM25 Okapi score |
| **Dense** | `kb_retriever.search_semantic()` — `all-MiniLM-L6-v2` sentence embeddings, ChromaDB cosine distance → score = `1/(1+distance)` | Normalized 0–1 similarity |
| **Hybrid** | `kb_retriever.search()` → `_rrf_merge()` — runs BM25 and Dense each at `top_n=2k`, merges via Reciprocal Rank Fusion: `score(d) = Σ 1/(60+rank_i)` | RRF score (not comparable to BM25/Dense scores) |

### Corpus

- **48 Singapore statute PDFs** in `corpus/raw/`
- **8,604 chunks** after paragraph-boundary chunking (800 token max, 15% overlap)
- Embeddings stored in ChromaDB (`storage/vector_store/`, collection `statutes`)

---

## 4. Results (Current: Run 3)

### Overall (n=142 scored, 58 excluded)

| Retriever | P@3 | Hit@3 | P@5 | Hit@5 |
|-----------|-----|-------|-----|-------|
| BM25 | 0.279 | 50.7% | 0.249 | 56.3% |
| Dense | 0.289 | 57.8% | 0.249 | 65.5% |
| **Hybrid** | **0.322** | **58.5%** | **0.293** | **72.5%** |

### Per Domain

**Employment** (n=72 scored, 2 excluded):

| Retriever | P@3 | Hit@3 | P@5 | Hit@5 |
|-----------|-----|-------|-----|-------|
| BM25 | 0.259 | 48.6% | 0.231 | 55.6% |
| Dense | 0.292 | 59.7% | 0.228 | 63.9% |
| **Hybrid** | **0.310** | **61.1%** | **0.267** | **75.0%** |

**PDPA** (n=60 scored, 4 excluded):

| Retriever | P@3 | Hit@3 | P@5 | Hit@5 |
|-----------|-----|-------|-----|-------|
| BM25 | 0.256 | 50.0% | 0.230 | 55.0% |
| Dense | 0.261 | 51.7% | 0.263 | 65.0% |
| **Hybrid** | **0.278** | **51.7%** | **0.283** | **66.7%** |

**Contract** (n=10 scored, 52 excluded — **treat with caution**):

| Retriever | P@3 | Hit@3 | P@5 | Hit@5 |
|-----------|-----|-------|-----|-------|
| BM25 | 0.567 | 70.0% | 0.500 | 70.0% |
| Dense | 0.433 | 80.0% | 0.320 | 80.0% |
| **Hybrid** | **0.667** | **80.0%** | **0.540** | **90.0%** |

---

## 5. Run Log

Each run is a complete execution of `eval/retrieval_benchmark.py` against the full 200-question benchmark. The results file (`eval/retrieval_results.json`) is overwritten each run.

### Run 1 — 2026-03-31 (v1 matching, naive BM25)
- **Matching:** v1 — full-text citation match (act name + section must appear literally in chunk body text)
- **BM25:** Naive word-frequency scoring with stopword filtering, distinct-match count, phrase boost
- **Results (overall k=3):** BM25 P@3=0.07 Hit@3=13% | Dense P@3=0.10 Hit@3=21% | Hybrid P@3=0.11 Hit@3=21%
- **Verdict:** Scores artificially low. Matching too strict — chunk text rarely contains the act's own name.

### Run 2 — 2026-03-31 (v2 matching, naive BM25)
- **Matching:** v2 — document filename match + relaxed section detection in text/heading (see §2 for details)
- **BM25:** Same naive word-frequency scoring
- **Results (overall k=3):** BM25 P@3=0.12 Hit@3=25% | Dense P@3=0.27 Hit@3=54% | Hybrid P@3=0.22 Hit@3=49%
- **Verdict:** Matching fixed. Dense 2x BM25. Hybrid underperforms dense — weak BM25 dilutes RRF fusion.

### Run 3 — 2026-04-01 (v2 matching, BM25 Okapi) ← CURRENT
- **Matching:** v2 — same as Run 2
- **BM25:** Upgraded to `rank_bm25.BM25Okapi` (TF-IDF with document length normalization, k1=1.5, b=0.75)
- **Results (overall k=3):** BM25 P@3=0.28 Hit@3=51% | Dense P@3=0.29 Hit@3=58% | Hybrid P@3=0.32 Hit@3=58%
- **Verdict:** BM25 doubled (0.12→0.28). Hybrid now properly wins at k=5 (Hit@5=73% vs Dense 65%). RRF fusion works as intended when both signals are strong.

### Run-over-run improvement (overall Hit@k)

| Retriever | Hit@3 R1→R2→R3 | Hit@5 R2→R3 |
|-----------|----------------|-------------|
| BM25 | 13% → 25% → **51%** | 35% → **56%** |
| Dense | 21% → 54% → **58%** | 63% → **65%** |
| Hybrid | 21% → 49% → **58%** | 61% → **73%** |

---

## 6. Interpretation

### BM25 Okapi vs naive word-frequency

The upgrade from naive word-frequency to BM25 Okapi doubled BM25 Hit@3 (25%→51%). Two key factors:
- **TF saturation:** BM25's `k1` parameter prevents long chunks from dominating via raw word counts. A word appearing 20 times scores only marginally more than 5 times.
- **Document length normalization:** The `b` parameter penalizes long chunks proportionally, preventing length bias that inflated naive scores for large chunks regardless of relevance.

### Why hybrid now wins

With proper BM25, the RRF fusion receives two meaningful rank signals instead of one strong (dense) and one noisy (naive BM25). At k=5, hybrid Hit@5=73% exceeds both BM25 (56%) and dense (65%) by 8–17 percentage points — the expected behavior for rank fusion with complementary signals.

### Why dense still edges out BM25 at k=3

Legal questions use everyday language ("I was fired without notice") while statutes use formal phrasing ("termination of contract of service"). Semantic embeddings bridge this vocabulary gap better than keyword matching, even with proper TF-IDF.

### Why contract scores are unreliable

52 of 62 contract questions reference "Common law" or acts not in the corpus. The 10 remaining questions are insufficient for statistical significance. This is a benchmark limitation, not a retrieval limitation.

### Why 58 questions were excluded

These questions reference:
- **Common law** principles (wrongful dismissal, breach of contract, privity, restraint of trade, guarantee)
- **Acts not in corpus** (Misrepresentation Act, Protection from Harassment Act, EU GDPR)
- **Non-statute sources** (PDPC Advisory Guidelines, PDPC Model AI Governance Framework)

These are correctly excluded — if the gold answer cites a source that doesn't exist in the corpus, no retriever could find it.

---

## 6. Limitations & Caveats

1. **BM25 fallback.** We use `rank_bm25.BM25Okapi` (TF-IDF with document length normalization). For very small corpora (<10 documents, e.g., in unit tests), BM25 IDF degenerates to zero, so we fall back to simple word-frequency counting. Production runs (8,604 chunks) always use true BM25.

2. **Binary recall only.** We cannot compute graded recall (e.g., "found 2 of 3 relevant chunks") because gold labels don't enumerate all relevant chunks. Our Hit@k metric is a lower bound on true recall.

3. **Section matching is heuristic.** The regex patterns target Singapore statute formatting but may miss unconventional numbering. A chunk containing the relevant legal text but formatted differently (e.g., schedule items, definitions sections) would be scored as irrelevant.

4. **Contract domain underpowered.** Only 10 of 62 contract questions are scoreable. Expanding the benchmark with statute-backed contract questions (e.g., referencing Unfair Contract Terms Act, Sale of Goods Act, Contracts (Rights of Third Parties) Act) would improve coverage.

5. **Embedding model.** We use `all-MiniLM-L6-v2` (384-dim, 22M params). A larger model like `all-mpnet-base-v2` (768-dim, 109M params) or a legal-domain-specific model may improve dense and hybrid scores.

6. **Exclusion rate.** 29% of questions excluded (58/200) is high. For the paper, report both the scored count and exclusion rate transparently.

---

## 7. Reproducing These Results

```bash
# 1. Ensure corpus is indexed
uv run python -m src.kb_cli ingest corpus/raw/

# 2. Run the benchmark
uv run python eval/retrieval_benchmark.py

# 3. Results appear at eval/retrieval_results.json
```

The benchmark is deterministic for BM25 (no randomness). Dense and hybrid results depend on the ChromaDB index state — ensure `storage/vector_store/` was built from the same 48-PDF corpus. The embedding model (`all-MiniLM-L6-v2`) is deterministic given the same input.

### Verifying a single question manually

To spot-check, run in Python:

```python
from src.kb_retriever import PDFKnowledgeBase

kb = PDFKnowledgeBase(path="corpus/raw")
kb.load_pdf()

# Dense retrieval for q001
results = kb.search_semantic("My employer fired me today without any notice", top_n=3)
for r in results:
    print(f"{r['document_name']} p.{r['page_number']} (score={r['score']:.4f})")
    print(f"  heading: {r.get('section_heading')}")
    print(f"  text: {r['text'][:150]}...")
    print()
```

Compare the output against gold: "Employment Act 1968, Section 11". Check whether any returned chunk is from `employment_act_1968.pdf` and contains "11.—" or "Section 11" in its text.
