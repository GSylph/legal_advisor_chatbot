# EVALUATION.md — Exact Experiment Protocol

> Follow this file step by step. Log every run in RESEARCH.md.
> Do not write results in the paper before running the corresponding experiment.

---

## Pre-Experiment Checklist

- [ ] `data/benchmark.json` exists with exactly 60 questions
- [ ] All 60 gold answers and gold statutes verified
- [ ] Gold chunk IDs annotated (for retrieval evaluation)
- [ ] `src/rules.py` implemented and all 20 rules passing `pytest src/tests/test_rules.py`
- [ ] `src/audit.py` implemented and passing `pytest src/tests/test_audit.py`
- [ ] ChromaDB index built (`python -m src.kb_cli index --path data/statutes --mode hybrid`)
- [ ] `GEMINI_API_KEY` in `.env`
- [ ] `eval/` directory exists (`mkdir -p eval`)

---

## Experiment Order

Run in this sequence — each depends on the previous being stable.

```
1. RAGAS automated metrics     (~30 min, no manual effort)
2. Retrieval quality           (~10 min, no manual effort)
3. Audit latency               (~5 min, no manual effort)
4. Hallucination annotation    (~2 hrs, 2 human annotators)
5. Explainability rubric       (~2 hrs, 2 human annotators)
6. Audit integrity demo        (~5 min, screenshot for paper)
```

---

## Experiment 1 — RAGAS

```bash
python src/benchmark.py --mode ragas --system ealai --output eval/ragas_ealai.json
python src/benchmark.py --mode ragas --system baseline --output eval/ragas_baseline.json
```

Extract from each output JSON:
- `faithfulness` → Table 1, rows 1
- `answer_relevancy` → Table 1, row 2
- `context_precision` → Table 1, row 3 (EALAI only; N/A for baseline)

Improvement column = EALAI score minus baseline score, rounded to 4 decimal places.

---

## Experiment 2 — Retrieval Quality

```bash
python src/benchmark.py --mode retrieval --output eval/retrieval_results.json
```

For each of 60 queries, retrieve top-3 chunks and compare `chunk_ids` to `gold_chunk_ids`:

```
Precision@3 = |retrieved ∩ gold| / 3
Recall@3    = |retrieved ∩ gold| / |gold|
```

Report per domain (employment / contract / PDPA) and overall.

---

## Experiment 3 — Audit Latency

```bash
python src/benchmark.py --mode latency --output eval/latency_results.json
```

Run 100 queries through full pipeline. Wrap `audit.log_interaction()` in a `time.perf_counter()` timer. Report:
- mean and std dev of audit-only latency (ms)
- mean total end-to-end latency (ms)
- audit as % of total

---

## Experiment 4 — Hallucination Annotation (Manual)

**Sample:** 15 EALAI responses + 15 baseline responses (same 15 questions for both)
**Output:** `eval/hallucination_annotation.csv`

**Definition of hallucinated (label = 1):**
A response contains at least one statutory reference, section number, or factual legal claim that is absent from or directly contradicted by the retrieved chunks or gold answer.

**When uncertain: label = 1 (conservative).**

**CSV schema:**
```csv
question_id,system,annotator_1,annotator_2,final_label,notes
q001,ealai,0,0,0,""
q001,baseline,1,1,1,"Cited non-existent Section 42 of Employment Act"
```

Final label = majority vote; disagreement defaults to 1.

**Rate = (sum of final_label for system) / 15 × 100**

---

## Experiment 5 — Explainability Rubric (Manual)

**Sample:** All 60 EALAI responses
**Output:** `eval/explainability_annotation.csv`
**Annotators:** 2 people, score independently

**Rubric (1–3 per dimension):**

| Dimension | 1 | 2 | 3 |
|---|---|---|---|
| Logical Completeness | No reasoning chain | Reasoning present but has gaps | Clear statute → conclusion chain |
| Citation Presence | No statute named | General law named only | Specific statute AND section named |
| Plain Language | Incomprehensible to layperson | Partially clear, has unexplained jargon | Fully understandable to non-lawyer |

**CSV schema:**
```csv
question_id,a1_complete,a1_cite,a1_plain,a2_complete,a2_cite,a2_plain
q001,3,3,2,3,2,2
```

**Compute scores:**
```python
from sklearn.metrics import cohen_kappa_score
import pandas as pd

df = pd.read_csv("eval/explainability_annotation.csv")
for dim, a1, a2 in [
    ("completeness", "a1_complete", "a2_complete"),
    ("citation", "a1_cite", "a2_cite"),
    ("plain", "a1_plain", "a2_plain"),
]:
    mean = ((df[a1] + df[a2]) / 2).mean()
    pct  = (((df[a1] + df[a2]) / 2) >= 2).mean() * 100
    k    = cohen_kappa_score(df[a1], df[a2])
    print(f"{dim}: mean={mean:.2f}, pct≥2={pct:.1f}%, kappa={k:.3f}")
```

---

## Experiment 6 — Audit Integrity Demo

Run this once. Screenshot the output for paper Section 5.5.

```python
import json, hashlib

with open("storage/logs/audit.jsonl") as f:
    entry = json.loads(f.readline())

original_hash = entry.pop("sha256")
entry["llm_answer"] = "TAMPERED: " + entry["llm_answer"]

raw = "|".join(str(v) for v in entry.values())
new_hash = hashlib.sha256(raw.encode()).hexdigest()

print("Original: ", original_hash)
print("Tampered: ", new_hash)
print("Match:    ", original_hash == new_hash)  # Must be False
```

---

## Filling [VALUE] Placeholders

After all experiments, update `RESEARCH.md` checkboxes first.
Then open `paper/EALAI_Paper_Draft.docx` and replace each `[VALUE]`.

**Rounding rules:**
- RAGAS scores: 4 decimal places (e.g., 0.8234)
- Rubric means and Kappa: 2 decimal places (e.g., 2.71)
- Percentages: 1 decimal place (e.g., 73.3%)
- Latency: 1 decimal place in ms (e.g., 12.4 ms)