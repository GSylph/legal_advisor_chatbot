"""T23 — Uncertainty calibration sweep (RQ4).

Runs 100 out-of-corpus (OOS) queries AND 100 in-corpus queries at
10 refusal thresholds. Computes refusal rate, false positive rate
(in-corpus wrongly refused), and false negative rate (OOS not refused).

Supports checkpointing: progress is saved after each query so the run
can resume after rate limits or interruptions.

Output: eval/calibration_results.csv
Checkpoint: eval/.checkpoint_calibration.json
"""

import csv
import json
from pathlib import Path

from src.chat_service import ChatService

OOS_PATH = Path("eval/oos_queries.jsonl")
BENCHMARK_PATH = Path("data/benchmark.json")
OUTPUT_PATH = Path("eval/calibration_results.csv")
CHECKPOINT_PATH = Path("eval/.checkpoint_calibration.json")
THRESHOLDS = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]


def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {}


def save_checkpoint(data: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(data, f, indent=2)


def load_oos_queries(limit: int = 100) -> list:
    queries = []
    with open(OOS_PATH) as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))
            if len(queries) >= limit:
                break
    return queries


def load_in_corpus_queries(limit: int = 100) -> list:
    with open(BENCHMARK_PATH) as f:
        benchmark = json.load(f)
    return benchmark[:limit]


def sweep_threshold(
    threshold: float,
    oos_queries: list,
    in_corpus_queries: list,
    service: ChatService,
    checkpoint: dict,
) -> dict:
    """Run both query sets at one threshold with checkpointing."""
    key = f"threshold_{threshold}"
    state = checkpoint.get(key, {
        "oos_completed": [],
        "oos_refused": 0,
        "ic_completed": [],
        "ic_refused": 0,
    })

    service.refusal_threshold = threshold

    oos_completed = set(state["oos_completed"])
    oos_refused = state["oos_refused"]
    ic_completed = set(state["ic_completed"])
    ic_refused = state["ic_refused"]

    # OOS queries — expect refusal
    for i, item in enumerate(oos_queries):
        qid = item.get("id", f"oos_{i}")
        if qid in oos_completed:
            continue
        try:
            structured, _ = service.run_turn(item["question"], retriever="hybrid")
            if structured.get("refused"):
                oos_refused += 1
        except Exception as exc:
            error_msg = str(exc)
            print(f"    OOS error: {error_msg}")
            if "keys exhausted" in error_msg.lower():
                print("\n  All API keys exhausted. Progress saved — rerun to resume.")
                return None
            continue

        oos_completed.add(qid)
        state = {
            "oos_completed": list(oos_completed),
            "oos_refused": oos_refused,
            "ic_completed": list(ic_completed),
            "ic_refused": ic_refused,
        }
        checkpoint[key] = state
        save_checkpoint(checkpoint)

    # In-corpus queries — expect answer
    for i, item in enumerate(in_corpus_queries):
        qid = item.get("id", f"ic_{i}")
        if qid in ic_completed:
            continue
        try:
            structured, _ = service.run_turn(item["question"], retriever="hybrid")
            if structured.get("refused"):
                ic_refused += 1
        except Exception as exc:
            error_msg = str(exc)
            print(f"    IC error: {error_msg}")
            if "keys exhausted" in error_msg.lower():
                print("\n  All API keys exhausted. Progress saved — rerun to resume.")
                return None
            continue

        ic_completed.add(qid)
        state = {
            "oos_completed": list(oos_completed),
            "oos_refused": oos_refused,
            "ic_completed": list(ic_completed),
            "ic_refused": ic_refused,
        }
        checkpoint[key] = state
        save_checkpoint(checkpoint)

    n_oos = max(len(oos_completed), 1)
    n_ic = max(len(ic_completed), 1)

    return {
        "threshold": threshold,
        "oos_refusal_rate": round(oos_refused / n_oos, 4),
        "false_negative_rate": round(1.0 - oos_refused / n_oos, 4),
        "false_positive_rate": round(ic_refused / n_ic, 4),
        "oos_completed": len(oos_completed),
        "oos_total": len(oos_queries),
        "ic_completed": len(ic_completed),
        "ic_total": len(in_corpus_queries),
    }


def main():
    if not OOS_PATH.exists():
        print(f"Error: {OOS_PATH} not found.")
        return
    if not BENCHMARK_PATH.exists():
        print(f"Error: {BENCHMARK_PATH} not found.")
        return

    oos_queries = load_oos_queries(100)
    in_corpus_queries = load_in_corpus_queries(100)
    print(f"Loaded {len(oos_queries)} OOS queries, {len(in_corpus_queries)} in-corpus queries")

    checkpoint = load_checkpoint()
    if checkpoint:
        done = sum(
            len(v.get("oos_completed", [])) + len(v.get("ic_completed", []))
            for v in checkpoint.values()
        )
        print(f"Resuming from checkpoint ({done} queries already completed)")

    service = ChatService(kb_path="corpus/raw")

    results = []
    for threshold in THRESHOLDS:
        key = f"threshold_{threshold}"
        existing = checkpoint.get(key, {})
        oos_done = len(existing.get("oos_completed", []))
        ic_done = len(existing.get("ic_completed", []))

        if oos_done >= len(oos_queries) and ic_done >= len(in_corpus_queries):
            print(f"\n=== Threshold: {threshold} === (already complete, skipping)")
            n_oos = max(oos_done, 1)
            n_ic = max(ic_done, 1)
            results.append({
                "threshold": threshold,
                "oos_refusal_rate": round(existing["oos_refused"] / n_oos, 4),
                "false_negative_rate": round(1.0 - existing["oos_refused"] / n_oos, 4),
                "false_positive_rate": round(existing["ic_refused"] / n_ic, 4),
                "oos_completed": oos_done,
                "oos_total": len(oos_queries),
                "ic_completed": ic_done,
                "ic_total": len(in_corpus_queries),
            })
            continue

        total_done = oos_done + ic_done
        total_needed = len(oos_queries) + len(in_corpus_queries)
        print(f"\n=== Threshold: {threshold} ({total_done}/{total_needed} done) ===")
        row = sweep_threshold(threshold, oos_queries, in_corpus_queries, service, checkpoint)
        if row is None:
            break
        results.append(row)
        print(f"  OOS refusal: {row['oos_refusal_rate']:.2%}, "
              f"FPR: {row['false_positive_rate']:.2%}, "
              f"FNR: {row['false_negative_rate']:.2%}")

    if results:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\nResults saved to {OUTPUT_PATH}")
    else:
        print("\nNo completed thresholds to write. Rerun when keys are available.")


if __name__ == "__main__":
    main()
