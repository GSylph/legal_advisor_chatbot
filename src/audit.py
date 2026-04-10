import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

AUDIT_LOG = Path("storage/logs/audit.jsonl")


def log_interaction(
    session_id: str,
    query: str,
    retrieved_context: List[Dict],   # from kb_retriever — list of {text, source, score}
    rule_result: Dict,                # from rules.check_consistency
    response_data: Dict,              # structured response dict from response_formatter
) -> str:
    """
    Appends a tamper-evident log entry. Returns the SHA-256 hash.
    The hash is computed BEFORE writing — any post-hoc tampering changes the hash.
    """
    chunk_sources = [c.get("document_name") or c.get("source", "") for c in retrieved_context]

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "query": query,
        "chunk_sources": chunk_sources,
        "rule_matched": rule_result.get("rule_matched"),
        "rule_statute": rule_result.get("statute"),
        "rule_section": rule_result.get("section"),
        "llm_applicable_law": response_data.get("applicable_law", ""),
        "llm_reasoning": response_data.get("reasoning", ""),
        "llm_answer": response_data.get("answer", ""),
        "consistency_flag": rule_result.get("consistent"),
    }

    # Hash all fields (excluding the hash itself) before writing
    # Use a stable sort of keys for consistency
    raw_parts = []
    for key in sorted(entry.keys()):
        raw_parts.append(str(entry[key]))
    
    raw = "|".join(raw_parts)
    sha256_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    entry["sha256"] = sha256_hash

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return sha256_hash


def get_session_log(session_id: str) -> List[Dict]:
    """Returns all audit entries for a given session_id."""
    if not AUDIT_LOG.exists():
        return []
    entries = []
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("session_id") == session_id:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def verify_entry(entry: Dict) -> bool:
    """Verifies a log entry has not been tampered with. Returns True if hash matches."""
    entry_copy = entry.copy()
    stored_hash = entry_copy.pop("sha256", None)
    
    raw_parts = []
    for key in sorted(entry_copy.keys()):
        raw_parts.append(str(entry_copy[key]))
    
    raw = "|".join(raw_parts)
    computed = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return stored_hash == computed
