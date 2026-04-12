# EALAI — Explainable and Auditable Legal AI

Legal advisory chatbot for Indian citizens combining RAG, symbolic reasoning, and cryptographic audit logging.

**Live Demo:** [link to be added after deployment]
**Paper:** JURIX 2025 / Legal NLP Workshop submission

---

## What it does

EALAI answers legal questions from Indian citizens in plain language by:
1. Retrieving relevant statutes from the ILDC corpus using dense semantic search
2. Generating a structured response with an explicit reasoning chain via Llama-3.1-8b
3. Validating the response against a symbolic rule engine covering Indian contract law and GDPR
4. Logging every interaction with a SHA-256 cryptographic hash for tamper-evident auditability

---

## Quickstart

```bash
git clone https://github.com/your-username/ealai
cd ealai
pip install -r requirements.txt
cp .env.example .env          # Add your GROQ_API_KEY
python backend/ingest.py      # Build FAISS index (run once)
uvicorn backend.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm start
```

---

## Project Structure

```
ealai/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── retrieval.py     # LlamaIndex + FAISS
│   ├── llm.py           # Groq API wrapper
│   ├── rules.py         # experta rule engine
│   ├── audit.py         # SHA-256 audit logger
│   ├── validator.py     # Input classifier
│   ├── benchmark.py     # RAGAS evaluation harness
│   └── ingest.py        # Corpus ingestion
├── frontend/src/
├── corpus/              # ILDC + EUR-Lex texts
├── data/                # FAISS index, benchmark, audit log
├── eval/                # Experiment results
└── docs/                # GEMINI.md, RESEARCH.md, SKILLS.md, etc.
```

---

## Symbolic Rules

The rule engine covers 20 rules across two domains. See [docs/RULES.md](docs/RULES.md) for the complete specification.

**Indian Contract / Employment Law (12 rules)**
- Wrongful termination without notice (Industrial Disputes Act S.25F)
- Fixed-term contract breach (Indian Contract Act S.73)
- Landlord entry without notice (Transfer of Property Act S.108)
- Wage withholding (Payment of Wages Act S.5)
- Non-compete enforceability (Indian Contract Act S.27)
- ... and 7 more

**GDPR / EU AI Act (8 rules)**
- Processing without lawful basis (GDPR Art.6)
- Right to erasure obligations (GDPR Art.17)
- High-risk AI conformity assessment (EU AI Act Art.43)
- ... and 5 more

---

## Evaluation

| Metric | EALAI | Baseline |
|---|---|---|
| Faithfulness (RAGAS) | [VALUE] | [VALUE] |
| Answer Relevancy (RAGAS) | [VALUE] | [VALUE] |
| Hallucination Rate | [VALUE]% | [VALUE]% |
| Precision@3 | [VALUE] | — |
| Recall@3 | [VALUE] | — |

*Fill after running `python backend/benchmark.py`*

---

## Corpus

- **Indian Legal Documents Corpus (ILDC):** Malik et al., ACL-IJCNLP 2021. ~500 filtered Supreme Court judgments.
- **EUR-Lex:** Official texts of GDPR (Regulation 2016/679) and EU AI Act (Regulation 2024/1689).

---

## Citation

```bibtex
@inproceedings{khan2025ealai,
  title={EALAI: An Explainable and Auditable Legal AI Framework for Indian Legal Advisory},
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