"""T12 — Retrieval-only benchmark: Precision@k / Recall@k across retrievers.

Evaluates whether top-k retrieved chunks come from the correct statute and
section for each benchmark question. No LLM calls required.

## Gold Matching Strategy (v2)

The initial version (v1) required the gold statute citation string (e.g.,
"Employment Act 1968, Section 11") to appear literally in the chunk body text.
This produced artificially low scores (P@3 ≈ 0.07–0.10, Hit@3 ≈ 0.13–0.21)
because raw PDF text rarely contains the act's own name — a chunk from Section
11 of the Employment Act just starts with "11.—(1) Either party to a contract
of service may…" without repeating "Employment Act 1968".

We evaluated six alternative matching strategies:

  1. Full-text citation match (v1) — too strict, false negatives from missing
     act name in body text. (P@3 ≈ 0.07)
  2. Document filename only — too lenient, any chunk from the right PDF counts.
  3. Document filename + raw section integer in text — small integers (4, 7)
     match page numbers and cross-references, high false positives.
  4. Document filename + Singapore statute section pattern — misses mid-section
     continuation chunks that lack the section header.
  5. Semantic similarity between gold answer and chunk — circular (tests
     retrieval with embeddings) and slow.
  6. Document filename + relaxed section detection in text OR heading —
     best balance of precision and recall.

**Selected: Approach 6.** A chunk is "relevant" when:
  (a) its `document_name` maps to the gold statute's act, AND
  (b) the section number appears in the chunk `text` (via statute-format
      patterns like `11.—` or `Section 11`) OR in the `section_heading` field.
  For gold entries without a section number, (a) alone suffices.
  For gold entries referencing "Common law" or other non-statute sources that
  have no corresponding corpus PDF, the question is excluded from scoring
  (documented as `n_excluded`).

Output: eval/retrieval_results.json
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.kb_retriever import PDFKnowledgeBase

BENCHMARK_PATH = Path("data/benchmark.json")
OUTPUT_PATH = Path("eval/retrieval_results.json")
RETRIEVERS = ["bm25", "dense", "hybrid"]
TOP_K_VALUES = [3, 5]


# ---------------------------------------------------------------------------
# Act name → PDF filename mapping
# ---------------------------------------------------------------------------

def _normalize_for_matching(name: str) -> str:
    """Lowercase, strip punctuation/parentheses, collapse whitespace."""
    name = name.lower()
    name = re.sub(r"[''()]", " ", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def build_act_to_filename_map(corpus_dir: str) -> Dict[str, str]:
    """Build a mapping from normalized act name fragments to PDF filenames.

    For example:
      "employment act 1968" → "employment_act_1968.pdf"
      "personal data protection act 2012" → "personal_data_protection_act_2012.pdf"
    """
    mapping: Dict[str, str] = {}
    for fname in os.listdir(corpus_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        # Convert filename to readable form: employment_act_1968.pdf → "employment act 1968"
        key = fname.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").lower()
        mapping[key] = fname
    return mapping


def resolve_act_to_filename(
    act_name: str, filename_map: Dict[str, str]
) -> Optional[str]:
    """Find the best-matching PDF filename for a gold act name.

    Returns None if the act has no corpus PDF (e.g., "Common law").
    """
    norm = _normalize_for_matching(act_name)

    # Direct match
    if norm in filename_map:
        return filename_map[norm]

    # Strip trailing year or amendment info and retry
    # "Employment Act 1968 (Amendment 2019)" → try "employment act 1968"
    stripped = re.sub(r"\s*(?:amendment|cap)\s*\d*\s*$", "", norm).strip()
    if stripped in filename_map:
        return filename_map[stripped]

    # Token-subset match: find filenames where every significant gold word appears
    norm_words = set(norm.split())
    # Remove very short/common words for matching
    norm_words -= {"act", "the", "of", "and", "for", "cap"}
    if not norm_words:
        norm_words = set(norm.split())

    best_match = None
    best_overlap = 0
    for key, fname in filename_map.items():
        key_words = set(key.split())
        overlap = len(norm_words & key_words)
        if overlap > best_overlap and overlap >= len(norm_words) * 0.6:
            best_overlap = overlap
            best_match = fname

    return best_match


# ---------------------------------------------------------------------------
# Gold statute parsing
# ---------------------------------------------------------------------------

def parse_gold_statute(gold_statute: str) -> List[Tuple[str, str]]:
    """Extract (act_name, section_number) pairs from gold_statute string.

    Examples:
      "Employment Act 1968, Section 11"         → [("Employment Act 1968", "11")]
      "CPFTA, Sections 4 and 7"                 → [("CPFTA", "4"), ("CPFTA", "7")]
      "PDPA, Section 13; Spam Control Act, S 6" → [("PDPA", "13"), ("Spam Control Act", "6")]
      "Common law (wrongful dismissal)"          → [("Common law (wrongful dismissal)", "")]
    """
    pairs = []
    parts = re.split(r";\s*", gold_statute)
    for part in parts:
        match = re.match(r"(.+?),?\s*[Ss]ections?\s+(.+)", part.strip())
        if match:
            act = match.group(1).strip()
            sections_str = match.group(2).strip()
            section_nums = re.findall(r"\d+[A-Za-z]*(?:\(\d+\))?", sections_str)
            for sec in section_nums:
                pairs.append((act, sec))
            if not section_nums:
                pairs.append((act, ""))
        else:
            # Check for "Part IX" style references
            match_part = re.match(r"(.+?),?\s*Part\s+(\w+)", part.strip())
            if match_part:
                pairs.append((match_part.group(1).strip(), ""))
            else:
                pairs.append((part.strip(), ""))
    return pairs


# ---------------------------------------------------------------------------
# Chunk relevance matching (v2)
# ---------------------------------------------------------------------------

def section_in_text(section_num: str, text: str) -> bool:
    """Check if a section number appears in text using statute formatting patterns."""
    text_lower = text.lower()
    sec = section_num.lower()

    patterns = [
        # Singapore statute format: "11.—(1)", "11.-(1)", "11. (1)"
        rf"\b{re.escape(sec)}\.[\s—\-]",
        # Explicit references: "section 11", "Section 11"
        rf"\bsection\s+{re.escape(sec)}\b",
        rf"\bsect\.?\s+{re.escape(sec)}\b",
        # Abbreviated: "s 11", "s.11", "s11("
        rf"\bs\.?\s*{re.escape(sec)}\b",
        # Section symbol
        rf"§\s*{re.escape(sec)}\b",
    ]
    return any(re.search(p, text_lower) for p in patterns)


def chunk_is_relevant(
    chunk: Dict,
    gold_pairs: List[Tuple[str, str]],
    filename_map: Dict[str, str],
) -> bool:
    """v2 matching: document_name matches gold act AND section found in text or heading."""
    chunk_doc = chunk.get("document_name", "")
    chunk_text = chunk.get("text", "")
    chunk_heading = chunk.get("section_heading") or ""

    for act_name, section_num in gold_pairs:
        expected_filename = resolve_act_to_filename(act_name, filename_map)
        if expected_filename is None:
            # No corpus PDF for this act — can't match
            continue
        if chunk_doc != expected_filename:
            continue

        # Document matches. If no section specified, that's sufficient.
        if not section_num:
            return True

        # Check section in chunk text or heading
        if section_in_text(section_num, chunk_text):
            return True
        if section_in_text(section_num, chunk_heading):
            return True

    return False


def gold_has_corpus_pdf(
    gold_pairs: List[Tuple[str, str]], filename_map: Dict[str, str]
) -> bool:
    """Return True if at least one gold act maps to a corpus PDF."""
    return any(
        resolve_act_to_filename(act, filename_map) is not None
        for act, _ in gold_pairs
    )


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_retriever(
    kb: PDFKnowledgeBase,
    benchmark: list,
    retriever: str,
    top_k: int,
    filename_map: Dict[str, str],
) -> Dict:
    """Compute Precision@k, Recall@k (binary), and Hit@k for one condition."""
    precisions = []
    recalls = []
    hits = 0
    excluded = 0

    for item in benchmark:
        question = item["question"]
        gold_pairs = parse_gold_statute(item["gold_statute"])

        # Skip questions whose gold statute has no corpus PDF
        if not gold_has_corpus_pdf(gold_pairs, filename_map):
            excluded += 1
            continue

        if retriever == "bm25":
            results = kb.search_keyword(question, top_n=top_k)
        elif retriever == "dense":
            results = kb.search_semantic(question, top_n=top_k)
        else:
            results = kb.search(question, top_n=top_k)

        relevant = sum(
            1 for chunk in results
            if chunk_is_relevant(chunk, gold_pairs, filename_map)
        )

        precision = relevant / top_k if top_k > 0 else 0.0
        recall = 1.0 if relevant > 0 else 0.0

        precisions.append(precision)
        recalls.append(recall)
        if relevant > 0:
            hits += 1

    n = max(len(precisions), 1)
    return {
        "retriever": retriever,
        "top_k": top_k,
        "mean_precision": round(sum(precisions) / n, 4),
        "mean_recall": round(sum(recalls) / n, 4),
        "hit_rate": round(hits / n, 4),
        "n_scored": len(precisions),
        "n_excluded": excluded,
        "n_questions": len(benchmark),
    }


def main():
    if not BENCHMARK_PATH.exists():
        print(f"Error: {BENCHMARK_PATH} not found.")
        return

    with open(BENCHMARK_PATH) as f:
        benchmark = json.load(f)

    print(f"Loaded {len(benchmark)} benchmark questions")

    kb = PDFKnowledgeBase(path="corpus/raw")
    kb.load_pdf()
    print(f"Loaded {len(kb.chunks)} chunks from corpus")

    filename_map = build_act_to_filename_map("corpus/raw")
    print(f"Built filename map with {len(filename_map)} PDFs")

    # Show which gold acts have no corpus match (for transparency)
    all_acts = set()
    for item in benchmark:
        for act, _ in parse_gold_statute(item["gold_statute"]):
            all_acts.add(act)
    unmapped = [a for a in sorted(all_acts) if resolve_act_to_filename(a, filename_map) is None]
    if unmapped:
        print(f"\nGold acts with no corpus PDF ({len(unmapped)} — excluded from scoring):")
        for a in unmapped:
            print(f"  - {a}")

    domains = sorted(set(item["domain"] for item in benchmark))
    all_results = []

    for retriever in RETRIEVERS:
        for top_k in TOP_K_VALUES:
            print(f"\n=== {retriever.upper()} @ k={top_k} ===")

            overall = evaluate_retriever(kb, benchmark, retriever, top_k, filename_map)
            overall["domain"] = "all"
            all_results.append(overall)
            print(f"  Overall: P@{top_k}={overall['mean_precision']:.4f}, "
                  f"R@{top_k}={overall['mean_recall']:.4f}, "
                  f"Hit@{top_k}={overall['hit_rate']:.4f} "
                  f"(scored={overall['n_scored']}, excluded={overall['n_excluded']})")

            for domain in domains:
                domain_items = [i for i in benchmark if i["domain"] == domain]
                result = evaluate_retriever(kb, domain_items, retriever, top_k, filename_map)
                result["domain"] = domain
                all_results.append(result)
                print(f"  {domain:12s}: P@{top_k}={result['mean_precision']:.4f}, "
                      f"R@{top_k}={result['mean_recall']:.4f}, "
                      f"Hit@{top_k}={result['hit_rate']:.4f} "
                      f"(scored={result['n_scored']}, excluded={result['n_excluded']})")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
