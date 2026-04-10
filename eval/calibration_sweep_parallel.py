"""T23 — Calibration sweep, parallelised across thresholds.

Runs the same logic as calibration_sweep.py but processes multiple thresholds
concurrently using a thread pool. Each worker gets its own ChatService instance
to avoid shared refusal_threshold state. Checkpoint writes are protected by a
lock so workers don't corrupt each other's progress.

Reads from and writes to the SAME checkpoint file as calibration_sweep.py
(eval/.checkpoint_calibration.json), so progress from a previous sequential
run is preserved and will be skipped.

Usage:
    uv run python eval/calibration_sweep_parallel.py            # default 4 workers
    uv run python eval/calibration_sweep_parallel.py --workers 3

Output: eval/calibration_results.csv
Checkpoint: eval/.checkpoint_calibration.json
"""

import argparse
import csv
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.chat_service import ChatService

OOS_PATH = Path("eval/oos_queries.jsonl")
BENCHMARK_PATH = Path("data/benchmark.json")
OUTPUT_PATH = Path("eval/calibration_results.csv")
CHECKPOINT_PATH = Path("eval/.checkpoint_calibration.json")
THRESHOLDS = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]

_checkpoint_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {}


def save_checkpoint(data: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Query loaders
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Worker: one threshold
# ---------------------------------------------------------------------------

def run_threshold(
    threshold: float,
    oos_queries: list,
    in_corpus_queries: list,
    checkpoint: dict,
) -> dict | None:
    """Process one threshold in a worker thread. Returns result dict or None if keys exhausted."""
    key = f"threshold_{threshold}"

    # Read initial state from checkpoint (shared dict, but we only read at start)
    with _checkpoint_lock:
        state = checkpoint.get(key, {
            "oos_completed": [],
            "oos_refused": 0,
            "ic_completed": [],
            "ic_refused": 0,
        })
        # Deep copy to avoid mutation races on the lists
        state = json.loads(json.dumps(state))

    # Each worker gets its own ChatService so refusal_threshold is isolated
    service = ChatService(kb_path="corpus/raw")
    service.refusal_threshold = threshold

    oos_completed = set(state["oos_completed"])
    oos_refused = state["oos_refused"]
    ic_completed = set(state["ic_completed"])
    ic_refused = state["ic_refused"]

    prefix = f"[t={threshold}]"

    # OOS queries — expect refusal (most won't hit the LLM)
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
            print(f"  {prefix} OOS error: {error_msg}")
            if "keys exhausted" in error_msg.lower():
                print(f"  {prefix} All API keys exhausted. Progress saved.")
                return None
            continue

        oos_completed.add(qid)
        with _checkpoint_lock:
            checkpoint[key] = {
                "oos_completed": list(oos_completed),
                "oos_refused": oos_refused,
                "ic_completed": list(ic_completed),
                "ic_refused": ic_refused,
            }
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
            print(f"  {prefix} IC error: {error_msg}")
            if "keys exhausted" in error_msg.lower():
                print(f"  {prefix} All API keys exhausted. Progress saved.")
                return None
            continue

        ic_completed.add(qid)
        with _checkpoint_lock:
            checkpoint[key] = {
                "oos_completed": list(oos_completed),
                "oos_refused": oos_refused,
                "ic_completed": list(ic_completed),
                "ic_refused": ic_refused,
            }
            save_checkpoint(checkpoint)

    n_oos = max(len(oos_completed), 1)
    n_ic = max(len(ic_completed), 1)

    result = {
        "threshold": threshold,
        "oos_refusal_rate": round(oos_refused / n_oos, 4),
        "false_negative_rate": round(1.0 - oos_refused / n_oos, 4),
        "false_positive_rate": round(ic_refused / n_ic, 4),
        "oos_completed": len(oos_completed),
        "oos_total": len(oos_queries),
        "ic_completed": len(ic_completed),
        "ic_total": len(in_corpus_queries),
    }
    print(f"  {prefix} DONE — OOS refusal: {result['oos_refusal_rate']:.2%}, "
          f"FPR: {result['false_positive_rate']:.2%}, "
          f"FNR: {result['false_negative_rate']:.2%}")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel threshold workers (default: 4)")
    args = parser.parse_args()

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

    # Find which thresholds still need work
    pending = []
    completed_results = []
    for threshold in THRESHOLDS:
        key = f"threshold_{threshold}"
        existing = checkpoint.get(key, {})
        oos_done = len(existing.get("oos_completed", []))
        ic_done = len(existing.get("ic_completed", []))
        if oos_done >= len(oos_queries) and ic_done >= len(in_corpus_queries):
            print(f"Threshold {threshold} already complete — skipping")
            n_oos = max(oos_done, 1)
            n_ic = max(ic_done, 1)
            completed_results.append({
                "threshold": threshold,
                "oos_refusal_rate": round(existing["oos_refused"] / n_oos, 4),
                "false_negative_rate": round(1.0 - existing["oos_refused"] / n_oos, 4),
                "false_positive_rate": round(existing["ic_refused"] / n_ic, 4),
                "oos_completed": oos_done,
                "oos_total": len(oos_queries),
                "ic_completed": ic_done,
                "ic_total": len(in_corpus_queries),
            })
        else:
            total_done = oos_done + ic_done
            total_needed = len(oos_queries) + len(in_corpus_queries)
            print(f"Threshold {threshold} pending ({total_done}/{total_needed} done)")
            pending.append(threshold)

    if not pending:
        print("All thresholds already complete.")
    else:
        n_workers = min(args.workers, len(pending))
        print(f"\nRunning {len(pending)} thresholds with {n_workers} parallel workers...")

        futures = {}
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            for threshold in pending:
                future = pool.submit(
                    run_threshold, threshold, oos_queries, in_corpus_queries, checkpoint
                )
                futures[future] = threshold

            for future in as_completed(futures):
                threshold = futures[future]
                try:
                    result = future.result()
                    if result is not None:
                        completed_results.append(result)
                except Exception as exc:
                    print(f"Worker for threshold {threshold} raised: {exc}")

    if completed_results:
        # Sort by threshold for clean CSV output
        completed_results.sort(key=lambda r: r["threshold"])
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=completed_results[0].keys())
            writer.writeheader()
            writer.writerows(completed_results)
        print(f"\nResults saved to {OUTPUT_PATH} ({len(completed_results)}/{len(THRESHOLDS)} thresholds)")
    else:
        print("\nNo completed thresholds to write. Rerun when keys are available.")


if __name__ == "__main__":
    main()
