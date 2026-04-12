# ARCHITECTURE.md — Authoritative System Design

> If your code contradicts this document, this document is wrong — update it.
> If you are unsure which is authoritative, read the actual source files first.

---

## Full System Pipeline

```
React Frontend (Vite + TailwindCSS)
  │  POST /api/chat
  ▼
FastAPI (src/api_server.py)
  │
  ├─► intent_classifier.py     ← classify: employment / contract / pdpa / general
  │
  ├─► entity_extractor.py      ← spaCy NER → extract entities
  │       (employment_type, notice_given, data_type, etc.)
  │
  ├─► kb_retriever.py          ← ChromaDB hybrid search (dense + sparse)
  │       top-3 chunks from data/statutes/ Singapore PDFs
  │       returns: [{text, source, score, metadata}]
  │
  ├─► prompt_builder.py        ← Jinja2: assemble query + context + history
  │       template: prompts/base_prompt.md
  │       output: structured prompt requiring APPLICABLE LAW / REASONING / ANSWER headers
  │
  ├─► api_client.py            ← Gemini API call (google-generativeai)
  │       model: gemini-pro (or current default)
  │       raw text response
  │
  ├─► response_formatter.py    ← parse raw → structured sections
  │       sections: Summary, Context, Steps, Warnings, Contacts, Disclaimer
  │       + applicable_law (EALAI addition)
  │
  ├─► rules.py [EALAI]         ← experta rule engine
  │       input: entities (from entity_extractor) + applicable_law (from formatter)
  │       output: {rule_matched, statute, section, consistent, confidence}
  │
  ├─► audit.py [EALAI]         ← SHA-256 append-only logger
  │       writes to: storage/logs/audit.jsonl
  │       returns: sha256 hash string
  │
  └─► response builder         ← assemble final JSON response
        adds: rule_result, audit_hash, warning if inconsistent
        returns to frontend

  │  GET /api/audit/{session_id}
  └─► audit.py:get_session_log → returns full trace

React Frontend
  ├─► Chat display
  └─► ReasoningTrace.jsx [EALAI]  ← collapsible panel per response
```

---

## Module Contracts

### `intent_classifier.py` (existing)
```
Input:  query: str
Output: intent: str — one of ["employment", "contract", "pdpa", "consumer", "general"]
```

### `entity_extractor.py` (existing)
```
Input:  query: str
Output: entities: dict
        Example: {
          "employment_type": "permanent",
          "notice_given": "false",
          "salary_above_threshold": "false"
        }
        Only keys determinable from the query are included.
```
> ⚠️ Read this file before implementing `_map_entities_to_attrs()` in `rules.py`.
> The exact output schema is the ground truth.

### `kb_retriever.py` (existing)
```
Input:  query: str, mode: str = "hybrid"
Output: list of dicts [{text: str, source: str, score: float, metadata: dict}]
        Always returns exactly 3 results (top_k=3)
```

### `prompt_builder.py` (existing, needs update)
```
Input:  query: str, context: list[dict], history: list[dict]
Output: str — final prompt for Gemini
Template: prompts/base_prompt.md (Jinja2)
UPDATE NEEDED: add APPLICABLE LAW / REASONING / ANSWER output format requirement
```

### `api_client.py` (existing — replace Gemini with Groq)
```
Input:  prompt: str
Output: str — raw LLM response text
Model:  llama-3.1-8b-instant via Groq API
Key:    GROQ_API_KEY in .env
Note:   Keep function signature call(prompt: str) -> str unchanged
        so chat_service.py requires zero edits after the swap.
```

### `response_formatter.py` (existing, needs update)
```
Input:  raw: str — Gemini response
Output: FormattedResponse object with fields:
        summary, context, steps, warnings, contacts, disclaimer
UPDATE NEEDED: add applicable_law field extraction
```

### `rules.py` (EALAI — build)
```
Input:  entities: dict, intent: str, llm_statute: str
Output: {
  rule_matched: bool,
  statute: str | None,
  section: str | None,
  violation: str | None,
  consistent: bool | None,    # None if no rule matched
  confidence: str             # "high" | "medium" | "low" | "none"
}
```

### `audit.py` (EALAI — build)
```
log_interaction(session_id, query, retrieved_context, rule_result, response) -> str (hash)
get_session_log(session_id) -> list[dict]
verify_entry(entry: dict) -> bool
```

---

## Storage Layout

```
storage/
├── vector_store/        ← ChromaDB persistent data (existing, do not touch)
└── logs/
    ├── errors.log           ← existing
    ├── fallback_responses.log ← existing
    └── audit.jsonl          ← EALAI addition (append-only)

data/
├── statutes/            ← Singapore statute PDFs (existing corpus)
└── benchmark.json       ← EALAI: 60 QA pairs for evaluation

eval/
├── ragas_ealai.json
├── ragas_baseline.json
├── retrieval_results.json
├── latency_results.json
└── hallucination_annotation.csv
```

---

## Audit Log Schema

Each line of `storage/logs/audit.jsonl` is one JSON object:

```json
{
  "timestamp": "2025-10-01T12:34:56.789Z",
  "session_id": "uuid4-string",
  "query": "original user query",
  "chunk_sources": ["Employment Act 1968 PDF", "PDPA 2012 PDF", "Contract Act PDF"],
  "rule_matched": true,
  "rule_statute": "Employment Act 1968",
  "rule_section": "Section 11",
  "llm_applicable_law": "Employment Act 1968, Section 11",
  "llm_reasoning": "step-by-step reasoning from Gemini",
  "llm_answer": "plain language answer",
  "consistency_flag": true,
  "sha256": "64-char hex hash of all preceding fields"
}
```

`sha256` is computed over `"|".join(str(v) for v in entry_without_sha256.values())`.

---

## Benchmark Schema (`data/benchmark.json`)

```json
[
  {
    "id": "q001",
    "domain": "employment",
    "question": "Can my employer terminate me without notice after 3 years?",
    "gold_answer": "Under Section 11 of the Employment Act 1968, ...",
    "gold_statute": "Employment Act 1968, Section 11",
    "gold_chunk_ids": ["ea_s11_para1", "ea_s10_para3"]
  }
]
```

Domain distribution: 25 employment, 20 contract, 15 PDPA. Total: 60.

---

## API Endpoints

| Method | Path | Handler | Status |
|---|---|---|---|
| GET | `/api/health` | health check | ✅ Existing |
| POST | `/api/chat` | `chat_service.process()` | ✅ Existing |
| GET | `/api/audit/{session_id}` | `audit.get_session_log()` | ❌ Add |

### POST `/api/chat` response (updated schema)

```json
{
  "session_id": "uuid4",
  "summary": "string",
  "context": "string",
  "steps": ["string"],
  "warnings": ["string"],
  "contacts": ["string"],
  "disclaimer": "string",
  "applicable_law": "string",
  "reasoning": "string",
  "rule_matched": true,
  "rule_statute": "Employment Act 1968",
  "rule_section": "Section 11",
  "consistency_flag": true,
  "warning": null,
  "audit_hash": "sha256-hex-string"
}
```

`warning` is non-null only when `consistency_flag = false`.

---

## Deployment

```
HuggingFace Spaces (Docker)              Vercel (free tier)
┌──────────────────────────┐             ┌──────────────────┐
│ FastAPI + ChromaDB       │◄──HTTPS─────│ React frontend   │
│ + Gemini API key (secret)│             │ (static build)   │
│ + audit.jsonl            │             └──────────────────┘
│ Port: 7860 (HF default)  │
└──────────────────────────┘
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY data/ ./data/
COPY storage/ ./storage/
ENV GROQ_API_KEY=""
CMD ["uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## Performance Constraints

| Constraint | Target | Why |
|---|---|---|
| End-to-end latency | < 4 seconds | Groq inference is fast (1–3s typical) |
| Audit overhead | < 50 ms | Paper claim: "negligible overhead" |
| ChromaDB index size | < 500 MB | HuggingFace Spaces free tier |
| RAM usage | < 2 GB | HuggingFace Spaces free tier |