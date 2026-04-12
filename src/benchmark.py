import json
import argparse
import os
import asyncio
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from src.chat_service import ChatService
from unittest.mock import MagicMock

BENCHMARK_PATH = Path("data/benchmark.json")
EVAL_DIR = Path("eval")

def run_ealai(question: str, service: ChatService):
    """Run the full EALAI pipeline."""
    structured, formatted = service.run_turn(question)
    # Extract contexts used
    # In our current setup, KB search happens inside run_turn.
    # We can retrieve them from the audit log or by repeating search.
    contexts = [c["text"] for c in service.kb.search(question)]
    return {
        "answer": structured.get("answer", formatted),
        "contexts": contexts
    }

def run_baseline(question: str, service: ChatService):
    """Run baseline: same model, NO retrieval context."""
    # Mock the KB to return empty results
    original_kb_search = service.kb.search
    service.kb.search = MagicMock(return_value=[])
    
    try:
        structured, formatted = service.run_turn(question)
        return {
            "answer": structured.get("answer", formatted),
            "contexts": [""] # RAGAS expects non-empty list
        }
    finally:
        # Restore original search
        service.kb.search = original_kb_search

async def run_evaluation(mode: str, system: str):
    EVAL_DIR.mkdir(exist_ok=True)
    if not BENCHMARK_PATH.exists():
        print(f"Error: Benchmark file {BENCHMARK_PATH} not found.")
        return

    with open(BENCHMARK_PATH, "r") as f:
        benchmark = json.load(f)

    service = ChatService(kb_path="corpus/raw")
    
    # Pre-load KB if needed
    try:
        service.kb.load_pdf()
    except:
        pass

    records = []
    print(f"Running {system.upper()} evaluation on {len(benchmark)} questions...")
    
    for i, item in enumerate(benchmark):
        print(f"[{i+1}/{len(benchmark)}] Question: {item['question'][:50]}...")
        if system == "ealai":
            result = run_ealai(item["question"], service)
        else:
            result = run_baseline(item["question"], service)

        records.append({
            "question": item["question"],
            "answer": result["answer"],
            "contexts": result["contexts"],
            "ground_truth": item["gold_answer"],
        })

    dataset = Dataset.from_list(records)
    
    # RAGAS evaluation
    # Note: RAGAS might need OpenAI/Groq keys for LLM-based metrics
    # If not provided, it might fail or use defaults.
    # We use the environment variables already set.
    
    print("Starting RAGAS evaluation...")
    try:
        # metrics = [faithfulness, answer_relevancy, context_precision]
        # Context precision needs retrieved contexts vs gold chunk ids or similar.
        # For simplicity in MVP, we use faithfulness and relevancy.
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy]
        )
        
        output_path = EVAL_DIR / f"ragas_{system}.json"
        results_dict = result.to_pandas().to_dict()
        with open(output_path, "w") as f:
            json.dump(results_dict, f, indent=2)

        print(f"\n=== RAGAS Results: {system.upper()} ===")
        print(result)
        return result
    except Exception as e:
        print(f"RAGAS evaluation failed: {e}")
        # Save records anyway for manual inspection
        output_path = EVAL_DIR / f"records_{system}.json"
        with open(output_path, "w") as f:
            json.dump(records, f, indent=2)
        print(f"Raw records saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["ragas", "retrieval", "latency"], default="ragas")
    parser.add_argument("--system", choices=["ealai", "baseline"], default="ealai")
    args = parser.parse_args()
    
    asyncio.run(run_evaluation(args.mode, args.system))
