"""Citation validity checker (T15).

Extracts [Act Name, Section X] citations from LLM output and verifies
each against the retrieved context chunks.
"""

import re
from typing import Any, Dict, List

# Matches patterns like [Employment Act 1968, Section 11] or [PDPA, Section 13]
CITATION_PATTERN = re.compile(
    r"\[([A-Za-z][A-Za-z\s()]+?(?:\d{4})?)\s*,\s*[Ss]ection\s+([\dA-Za-z]+(?:\([a-z0-9]+\))?)\]"
)


def extract_citations(text: str) -> List[Dict[str, str]]:
    """Extract all [Act Name, Section X] citations from text."""
    citations = []
    for match in CITATION_PATTERN.finditer(text):
        citations.append({
            "act": match.group(1).strip(),
            "section": match.group(2).strip(),
            "raw": match.group(0),
        })
    return citations


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for fuzzy matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def verify_citations(
    answer_text: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Check each citation in the answer against retrieved chunks.

    Returns dict with valid_citations, hallucinated_citations, and
    citation_accuracy (valid / total, or 1.0 if no citations found).
    """
    citations = extract_citations(answer_text)

    if not citations:
        return {
            "valid_citations": [],
            "hallucinated_citations": [],
            "citation_accuracy": 1.0,
        }

    # Build a searchable corpus from retrieved chunk texts
    chunk_texts = [_normalize(c.get("text", "")) for c in retrieved_chunks]
    corpus = " ".join(chunk_texts)

    valid: List[str] = []
    hallucinated: List[str] = []

    for cite in citations:
        act_norm = _normalize(cite["act"])
        section_norm = cite["section"].lower()

        # Check if the act name appears in the retrieved context
        act_found = act_norm in corpus
        # Check if the section number appears near the act reference
        section_found = f"section {section_norm}" in corpus or f"s.{section_norm}" in corpus or f"s {section_norm}" in corpus

        if act_found and section_found:
            valid.append(cite["raw"])
        else:
            hallucinated.append(cite["raw"])

    total = len(valid) + len(hallucinated)
    return {
        "valid_citations": valid,
        "hallucinated_citations": hallucinated,
        "citation_accuracy": len(valid) / total if total > 0 else 1.0,
    }
