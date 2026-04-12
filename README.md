# EALAI — Explainable and Auditable Legal AI

A research system for Singapore law (PDPA, Employment Act 1968, Contract/Consumer law) combining retrieval-augmented generation, a symbolic rule engine, and cryptographic audit logging. Targeting JURIX 2025.

**Live Demo:** [link to be added after deployment]
**Paper:** JURIX 2025 · Springer LNCS

---

## What it does

EALAI answers Singapore legal questions in plain language by:

1. **Retrieving** relevant statute chunks from 48 Singapore PDFs using hybrid BM25 + dense vector search (ChromaDB)
2. **Generating** a structured response with explicit reasoning via Llama-3.1-8b (Groq)
3. **Validating** the response against 20 symbolic IF-THEN rules covering Employment Act, Contract Law, and PDPA
4. **Logging** every interaction with a SHA-256 cryptographic hash for tamper-evident auditability

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A free [Groq API key](https://console.groq.com)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ealai
cd ealai
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Groq key:

```
GROQ_API_KEY=gsk_your_key_here
```

If you hit the Groq free-tier daily token limit, add extra keys from different accounts:

```
GROQ_API_KEY=gsk_abc...
GROQ_API_KEY_2=gsk_def...
GROQ_API_KEY_3=gsk_ghi...
```

The API client auto-rotates keys on daily limit errors.

### 3. Install Python dependencies

```bash
uv sync
```

### 4. Build the knowledge base

Ingest the 48 Singapore statute PDFs into ChromaDB (run once, or after adding new PDFs):

```bash
uv run python -m src.kb_cli ingest corpus/raw/
```

This takes 2–5 minutes on first run. The vector store is saved to `storage/vector_store/`.

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the app

You need two terminals — one for the backend, one for the frontend.

**Terminal 1 — Backend:**

```bash
uv run uvicorn src.api_server:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

> The frontend shows a "Backend offline" banner until the backend is ready. Wait for uvicorn to finish loading the vector store before sending a query.

---

## Knowledge base CLI

```bash
# Ingest PDFs into ChromaDB
uv run python -m src.kb_cli ingest corpus/raw/

# Test retrieval
uv run python -m src.kb_cli search "wrongful termination notice period"

# Show index stats
uv run python -m src.kb_cli stats
```

---

## Running tests

```bash
uv run pytest                                              # all tests
uv run pytest src/tests/test_rules.py                     # symbolic rule engine
uv run pytest src/tests/test_audit.py                     # audit log tamper detection
uv run pytest src/tests/test_audit.py::test_tamper_detection
```

---

## Running evaluations

All eval scripts support checkpointing — they resume from where they left off after interruptions.

```bash
# T12: Retrieval P@k / Hit@k → eval/retrieval_results.json
uv run python eval/retrieval_benchmark.py

# T22: End-to-end 4-condition eval (200 questions) → eval/results_phase1.csv
uv run python eval/run_eval.py

# T23: Refusal threshold calibration sweep → eval/calibration_results.csv
uv run python eval/calibration_sweep.py

# T25: Generate paper figures → paper/figures/
uv run python eval/make_figures.py
```

---

## Project structure

```
ealai/
├── src/
│   ├── api_server.py         # FastAPI app — /api/chat, /api/chat/stream, /api/audit
│   ├── chat_service.py       # Main pipeline orchestrator
│   ├── api_client.py         # Groq API wrapper with retry + key rotation
│   ├── kb_retriever.py       # ChromaDB hybrid retrieval (BM25 + dense)
│   ├── vector_store.py       # ChromaDB wrapper
│   ├── intent_classifier.py  # Query intent classification
│   ├── entity_extractor.py   # spaCy NER
│   ├── prompt_builder.py     # Jinja2 prompt assembly
│   ├── response_formatter.py # Structured section parser
│   ├── rules.py              # SingaporeLegalEngine — 20 symbolic rules
│   ├── audit.py              # SHA-256 append-only audit logger
│   ├── benchmark.py          # RAGAS evaluation harness
│   ├── citation_checker.py   # Citation accuracy checker
│   └── kb_cli.py             # Knowledge base CLI
├── frontend/
│   ├── src/
│   │   ├── pages/            # LandingPage, ProfilePage
│   │   ├── components/
│   │   │   ├── Chat.jsx      # Streaming chat with SSE
│   │   │   ├── ReasoningTrace.jsx
│   │   │   ├── MarkdownMessage.jsx
│   │   │   ├── landing/      # 6 landing page sections
│   │   │   └── profile/      # 5 profile page sections
│   │   └── hooks/            # useIntersectionObserver, useCountUp
│   └── tailwind.config.cjs
├── corpus/raw/               # 48 Singapore statute PDFs
├── prompts/base_prompt.md    # LLM prompt template
├── storage/
│   ├── vector_store/         # ChromaDB (built by kb_cli ingest)
│   └── logs/audit.jsonl      # Append-only audit log
├── eval/                     # Benchmark scripts and results
├── paper/                    # JURIX 2025 LaTeX draft + figures
├── data/benchmark.json       # 200 QA pairs (74 employment, 62 contract, 64 PDPA)
└── pyproject.toml
```

---

## Symbolic rules

20 IF-THEN rules across three domains. See [`RULES.md`](RULES.md) for the full specification.

| Domain | Rules | Example |
|---|---|---|
| Employment Act 1968 | 1–8 | Wrongful termination without notice → EA S.11 |
| Contract Law | 9–12 | Consideration absent → contract unenforceable |
| PDPA 2012 | 13–20 | Data collected without consent → PDPA S.13 |

---

## Evaluation results

**T12 — Retrieval (n=142):**

| Retriever | P@3 | Hit@3 | P@5 | Hit@5 |
|---|---|---|---|---|
| BM25 | 0.279 | 50.7% | 0.249 | 56.3% |
| Dense | 0.289 | 57.8% | 0.249 | 65.5% |
| **Hybrid** | **0.322** | **58.5%** | **0.293** | **72.5%** |

**T22 — End-to-end hallucination (n=200):**

| Retriever | Hallucination Rate | Citation Accuracy |
|---|---|---|
| None (baseline) | 42% | 0.580 |
| BM25 | 22% | 0.784 |
| **Dense** | **20%** | **0.800** |
| Hybrid | 36% | 0.645 |

**T23 — Recommended refusal threshold: 0.45** (OOS refusal 11%, false positive 3%)

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness check |
| `POST` | `/api/chat` | Standard chat (full response) |
| `POST` | `/api/chat/stream` | Streaming chat (SSE token-by-token) |
| `GET` | `/api/audit/{session_id}` | Audit log for a session |

---

## Citation

```bibtex
@inproceedings{khan2025ealai,
  title={EALAI: An Explainable and Auditable Legal AI Framework
         with Empirical Evaluation on Singapore Statutory Law},
  author={Khan, Mohammed Iqbal},
  booktitle={Proceedings of JURIX 2025},
  year={2025},
  publisher={Springer LNCS}
}
```

---

## Disclaimer

This system is a research prototype. Outputs are not legal advice. Always consult a qualified legal professional for your specific situation.

## License

MIT
