# RESEARCH.md — Paper Status & Results Tracker

> Update this file after every experiment. This is the live source of truth for submission readiness.
> When all rows in a group show ✅, that group is done.

---

## Paper Status

| Field | Value |
|---|---|
| Title | EALAI: An Explainable and Auditable Legal AI Framework — System Implementation and Empirical Evaluation |
| Jurisdiction | Singapore (PDPA, Employment Act, Contract law) |
| Format | LNCS (Springer) |
| Target | JURIX 2025 / Legal NLP Workshop |
| Draft file | `paper/EALAI_Paper_Draft.docx` |
| Current status | Draft written — awaiting experimental results |

---

## Section Completion

| Section | Written | [VALUE]s Filled | Ready |
|---|---|---|---|
| Abstract | ✅ | ❌ | ❌ |
| 1. Introduction | ✅ | ✅ | ✅ |
| 2. Related Work | ✅ | ✅ | ✅ |
| 3. System Architecture | ✅ | ✅ | ✅ |
| 4. Evaluation Protocol | ✅ | ✅ | ✅ |
| 5. Results | ✅ | ❌ | ❌ |
| 6. Discussion | ✅ | ❌ | ❌ |
| 7. Conclusion | ✅ | ✅ | ✅ |
| References | ✅ | verify links | ❌ |

---

## [VALUE] Placeholder Tracker

### Group A — RAGAS (run `python src/benchmark.py --mode ragas`)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| EALAI Faithfulness | Abstract, Table 1 | ❌ | — |
| Baseline Faithfulness | Abstract, Table 1 | ❌ | — |
| EALAI Answer Relevancy | Table 1 | ❌ | — |
| Baseline Answer Relevancy | Table 1 | ❌ | — |
| EALAI Context Precision | Table 1 | ❌ | — |
| Faithfulness improvement | Table 1 (col 4) | ❌ | — |

### Group B — Hallucination (manual annotation, n=30)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| EALAI Hallucination Rate % | Abstract, Table 1, Sec 5.1 | ❌ | — |
| Baseline Hallucination Rate % | Abstract, Table 1, Sec 5.1 | ❌ | — |
| Reduction in pp | Table 1, Sec 5.1 | ❌ | — |

### Group C — Explainability Rubric (manual annotation, n=60)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| Logical Completeness mean | Table 2 | ❌ | — |
| Logical Completeness Kappa | Table 2 | ❌ | — |
| Logical Completeness % ≥ 2 | Table 2 | ❌ | — |
| Citation Presence mean | Table 2 | ❌ | — |
| Citation Presence Kappa | Table 2 | ❌ | — |
| Citation Presence % ≥ 2 | Table 2 | ❌ | — |
| Plain Language mean | Table 2 | ❌ | — |
| Plain Language Kappa | Table 2 | ❌ | — |
| Plain Language % ≥ 2 | Table 2 | ❌ | — |

### Group D — Retrieval Quality (run `python src/benchmark.py --mode retrieval`)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| Employment Precision@3 | Table 3 | ❌ | — |
| Employment Recall@3 | Table 3 | ❌ | — |
| Contract Precision@3 | Table 3 | ❌ | — |
| Contract Recall@3 | Table 3 | ❌ | — |
| PDPA Precision@3 | Table 3 | ❌ | — |
| PDPA Recall@3 | Table 3 | ❌ | — |
| Overall Precision@3 | Table 3, Sec 5.3 | ❌ | — |
| Overall Recall@3 | Table 3, Sec 5.3 | ❌ | — |

### Group E — Audit Latency (run `python src/benchmark.py --mode latency`)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| Mean audit latency (ms) | Sec 5.4 | ❌ | — |
| Latency std dev (ms) | Sec 5.4 | ❌ | — |
| Audit latency as % of total | Sec 5.4 | ❌ | — |
| Mean total response time (ms) | Sec 5.4 | ❌ | — |

### Group F — Narrative Inline Values

| Placeholder | Location | Source | Status |
|---|---|---|---|
| "accounting for [VALUE] of 60 queries" | Sec 5.2 | Count unmatched rule queries | ❌ |
| Kappa range "[VALUE] to [VALUE]" | Sec 5.2 | Min/max Kappa from Table 2 | ❌ |

---

## Benchmark Construction Log

```
File: data/benchmark.json
Total questions: 60
Composition:
  - Employment / termination (Singapore EA): 25 questions
  - Contract law (misrepresentation, breach):  20 questions
  - PDPA / data protection:                    15 questions

Annotation:
  Annotator 1: [NAME]
  Annotator 2: [NAME]
  Disagreement resolution: discussion to consensus
  Date created: [DATE]

Schema per entry:
{
  "id": "q001",
  "domain": "employment",
  "question": "...",
  "gold_answer": "...",
  "gold_statute": "Employment Act 1968, Section 11",
  "gold_chunk_ids": ["statute_EA_s11_para2", "..."]
}
```

---

## References Verification

| # | Citation | Verified |
|---|---|---|
| 1 | Ogunsan & Johnson (2025) — Limitations of Legal Chatbots | ❌ |
| 2 | Hagan (2021) — DoNotPay and Beyond | ❌ |
| 3 | Lewis et al. (2020) — RAG | https://arxiv.org/abs/2005.11401 | ❌ |
| 4 | Guu et al. (2020) — REALM | https://arxiv.org/abs/2002.08909 | ❌ |
| 5 | Karamcheti et al. (2024) — LLMs in Law | https://arxiv.org/abs/2406.04136 | ❌ |
| 6 | Zheng et al. (2023) — DISC-LawLLM | https://arxiv.org/abs/2309.11325 | ❌ |
| 7 | Malik et al. (2021) — ILDC | ACL-IJCNLP 2021 | ❌ |
| 8 | Hamilton et al. (2023) — Neuro-Symbolic Legal NLP | Natural Language Engineering | ❌ |
| 9 | Floridi (2019) — Digital Ethics | Philosophy & Technology | ❌ |
| 10 | PDPC Singapore (2020) — Model AI Governance Framework | https://www.pdpc.gov.sg | ❌ |
| 11 | Singapore PDPA (2012, amended 2021) | https://sso.agc.gov.sg | ❌ |
| 12 | Susskind (2017) — Tomorrow's Lawyers | Oxford University Press | ❌ |
| 13 | Surden (2019) — AI and Law | Georgia State Law Review | ❌ |
| 14 | Es et al. (2023) — RAGAS | https://arxiv.org/abs/2309.15217 | ❌ |

> Mark ✅ only after clicking the link and confirming the paper title + authors match exactly.

---

## Group G — Calibration Sweep (T23)

| Placeholder | Paper Location | Status | Actual Value |
|---|---|---|---|
| Recommended refusal threshold | Sec 5 / RQ4 | ✅ | 0.45 |
| OOS refusal rate @ recommended threshold | Sec 5 / RQ4 | ✅ | 11% |
| False positive rate @ recommended threshold | Sec 5 / RQ4 | ✅ | 3% |
| False negative rate @ recommended threshold | Sec 5 / RQ4 | ✅ | 89% |

**Full sweep results (n=100 OOS + 100 in-corpus per threshold):**

| Threshold | OOS Refusal Rate | False Negative Rate | False Positive Rate |
|-----------|-----------------|---------------------|---------------------|
| 0.20 | 0% | 100% | 0% |
| 0.25 | 0% | 100% | 0% |
| 0.30 | 0% | 100% | 0% |
| 0.35 | 0% | 100% | 0% |
| 0.40 | 8% | 92% | 0% |
| **0.45** | **11%** | **89%** | **3%** |
| 0.50 | 39% | 61% | 32% |
| 0.55 | 65% | 35% | 61% |
| 0.60 | 91% | 9% | 84% |
| 0.70 | 100% | 0% | 98% |

**Interpretation:** Sharp precision cliff between 0.45 and 0.50 — FP rate jumps from 3% to 32% for only a 28pp gain in OOS recall. Threshold 0.45 dominates: zero false positives at 0.40, acceptable 3% FP at 0.45 with first meaningful OOS refusal. Recommended operating point: **0.45**.

---

## Experiment Run Log

| Date | Experiment | Script | Key Result | Notes |
|---|---|---|---|---|
| 2026-04-06 | T22 — 4-condition eval | `eval/run_eval.py` | Dense best: 20% hallucination, 0.800 citation acc | 200Q × 4 conditions = 800 LLM calls |
| 2026-04-06 | T23 — Calibration sweep | `eval/calibration_sweep.py` | Recommended threshold: 0.45 (11% OOS, 3% FP) | 10 thresholds × 200 queries = 2000 LLM calls |
| 2026-04-06 | T25 — Paper figures | `eval/make_figures.py` | All 4 outputs written to paper/figures/ | fig1 (refusal curve) + fig2 (eval summary) at 300 DPI |