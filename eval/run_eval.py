"""T22 — Phase 1 evaluation: 4 conditions × full benchmark.

Runs every benchmark question through the pipeline with each retriever
mode (none / bm25 / dense / hybrid) and computes:
  - hallucination_rate  (% answers with ≥1 hallucinated citation)
  - citation_accuracy   (mean valid / total citations)
  - mean_latency_ms     (average end-to-end latency)

Supports checkpointing: progress is saved after each question so the run
can resume after rate limits or interruptions.

Output: eval/results_phase1.csv
Checkpoint: eval/.checkpoint_phase1.json
"""

import csv
import json
import time
from pathlib import Path

from src.chat_service import ChatService
from src.citation_checker import verify_citations

BENCHMARK_PATH = Path("data/benchmark.json")
OUTPUT_PATH = Path("eval/results_phase1.csv")
CHECKPOINT_PATH = Path("eval/.checkpoint_phase1.json")
RETRIEVERS = ["none", "bm25", "dense", "hybrid"]


def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {}


def save_checkpoint(data: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(data, f, indent=2)


def run_condition(
    retriever: str, benchmark: list, service: ChatService, checkpoint: dict
) -> dict:
    """Run all benchmark questions for one retriever condition with checkpointing."""
    key = f"condition_{retriever}"
    state = checkpoint.get(key, {
        "completed": [],
        "hallucinated_count": 0,
        "citation_accuracies": [],
        "latencies": [],
    })
    completed_ids = set(state["completed"])
    hallucinated_count = state["hallucinated_count"]
    citation_accuracies = state["citation_accuracies"]
    latencies = state["latencies"]
    total = len(benchmark)

    for i, item in enumerate(benchmark):
        qid = item.get("id", str(i))
        if qid in completed_ids:
            continue

        question = item["question"]
        print(f"  [{len(completed_ids) + 1}/{total}] {question[:60]}...")

        t0 = time.monotonic()
        try:
            structured, formatted = service.run_turn(
                question, retriever=retriever
            )
        except Exception as exc:
            error_msg = str(exc)
            print(f"    ERROR: {error_msg}")
            if "keys exhausted" in error_msg.lower():
                print("\n  All API keys exhausted. Progress saved — rerun to resume.")
                return None
            continue
        latency_ms = (time.monotonic() - t0) * 1000
        latencies.append(latency_ms)

        # Citation check against retrieved chunks
        answer_text = structured.get("answer", formatted)
        chunks = service.kb.search(question) if retriever != "none" else []
        cite_result = verify_citations(answer_text, chunks)

        citation_accuracies.append(cite_result["citation_accuracy"])
        if cite_result["hallucinated_citations"]:
            hallucinated_count += 1

        completed_ids.add(qid)

        # Save checkpoint after each question
        state = {
            "completed": list(completed_ids),
            "hallucinated_count": hallucinated_count,
            "citation_accuracies": citation_accuracies,
            "latencies": latencies,
        }
        checkpoint[key] = state
        save_checkpoint(checkpoint)

    n = max(len(latencies), 1)
    return {
        "retriever": retriever,
        "n_questions": total,
        "n_completed": len(completed_ids),
        "hallucination_rate": round(hallucinated_count / max(len(completed_ids), 1), 4),
        "citation_accuracy": round(sum(citation_accuracies) / n, 4),
        "mean_latency_ms": round(sum(latencies) / n, 1),
    }


def main():
    if not BENCHMARK_PATH.exists():
        print(f"Error: {BENCHMARK_PATH} not found.")
        return

    with open(BENCHMARK_PATH) as f:
        benchmark = json.load(f)

    checkpoint = load_checkpoint()
    if checkpoint:
        done = sum(len(v.get("completed", [])) for v in checkpoint.values())
        print(f"Resuming from checkpoint ({done} questions already completed)")

    service = ChatService(kb_path="corpus/raw")

    results = []
    for retriever in RETRIEVERS:
        key = f"condition_{retriever}"
        existing = checkpoint.get(key, {})
        completed = len(existing.get("completed", []))
        if completed >= len(benchmark):
            print(f"\n=== Condition: {retriever.upper()} === (already complete, skipping)")
            # Rebuild result from checkpoint
            n = max(len(existing["latencies"]), 1)
            results.append({
                "retriever": retriever,
                "n_questions": len(benchmark),
                "n_completed": completed,
                "hallucination_rate": round(existing["hallucinated_count"] / max(completed, 1), 4),
                "citation_accuracy": round(sum(existing["citation_accuracies"]) / n, 4),
                "mean_latency_ms": round(sum(existing["latencies"]) / n, 1),
            })
            continue

        print(f"\n=== Condition: {retriever.upper()} ({completed}/{len(benchmark)} done) ===")
        row = run_condition(retriever, benchmark, service, checkpoint)
        if row is None:
            # Keys exhausted — stop gracefully
            break
        results.append(row)
        print(f"  → hallucination_rate={row['hallucination_rate']}, "
              f"citation_accuracy={row['citation_accuracy']}, "
              f"latency={row['mean_latency_ms']}ms "
              f"({row['n_completed']}/{row['n_questions']} completed)")

    if results:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        with open(OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\nResults saved to {OUTPUT_PATH}")
    else:
        print("\nNo completed conditions to write. Rerun when keys are available.")

    # Clean up checkpoint if all conditions completed
    all_done = all(
        len(checkpoint.get(f"condition_{r}", {}).get("completed", [])) >= len(benchmark)
        for r in RETRIEVERS
    )
    if all_done:
        print("All conditions complete. Checkpoint retained for reference.")


if __name__ == "__main__":
    main()
