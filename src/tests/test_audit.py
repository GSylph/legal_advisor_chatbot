import json
import pytest
from pathlib import Path
from src import audit

def test_audit_logging(tmp_path, monkeypatch):
    # Mock the AUDIT_LOG path to use a temporary directory
    mock_log = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG", mock_log)
    
    session_id = "test-session-123"
    query = "How do I protect my personal data?"
    context = [{"source": "pdpa_statute.pdf", "text": "Data protection rules...", "score": 0.9}]
    rule_result = {"rule_matched": True, "statute": "PDPA 2012", "consistent": True}
    response_data = {
        "applicable_law": "PDPA 2012", 
        "reasoning": "Step 1: check consent...", 
        "answer": "You need consent."
    }
    
    # Log the interaction
    hash_val = audit.log_interaction(session_id, query, context, rule_result, response_data)
    assert len(hash_val) == 64 # SHA-256 hex length
    
    # Retrieve the log for the session
    entries = audit.get_session_log(session_id)
    assert len(entries) == 1
    assert entries[0]["query"] == query
    assert entries[0]["sha256"] == hash_val
    
    # Verify the integrity of the entry
    assert audit.verify_entry(entries[0]) is True

def test_tamper_detection(tmp_path, monkeypatch):
    # Mock the AUDIT_LOG path
    mock_log = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG", mock_log)
    
    # Create a legitimate log entry
    audit.log_interaction("session-x", "original query", [], {"rule_matched": False}, {})
    
    # Read the entry from the file
    with open(mock_log, "r", encoding="utf-8") as f:
        entry = json.loads(f.read().strip())
    
    # Tamper with the query content
    entry["query"] = "tampered query"
    
    # Verification should now fail
    assert audit.verify_entry(entry) is False
