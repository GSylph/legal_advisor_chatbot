"""T25 — Generate paper figures and tables.

Reads evaluation CSVs and produces:
  1. paper/figures/table2_hallucination.csv
  2. paper/figures/table3_retrieval_ablation.csv
  3. paper/figures/fig1_refusal_curve.png
  4. paper/figures/fig2_evaluation_summary.png

Run after eval/results_phase1.csv and eval/calibration_results.csv exist.
"""

import csv
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

EVAL_DIR = Path("eval")
FIGURES_DIR = Path("paper/figures")


def ensure_dirs():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ── Table 2: Hallucination rates across 4 conditions ──


def make_table2():
    src = EVAL_DIR / "results_phase1.csv"
    if not src.exists():
        print(f"Skipping table2: {src} not found")
        return
    df = pd.read_csv(src)
    out = df[["retriever", "hallucination_rate", "citation_accuracy", "mean_latency_ms"]]
    dest = FIGURES_DIR / "table2_hallucination.csv"
    out.to_csv(dest, index=False)
    print(f"Written {dest}")


# ── Table 3: Retrieval ablation (Precision@3, Recall@3 per domain) ──


def make_table3():
    src = EVAL_DIR / "retrieval_results.json"
    if not src.exists():
        print(f"Skipping table3: {src} not found")
        return
    with open(src) as f:
        data = pd.DataFrame(json.load(f))
    dest = FIGURES_DIR / "table3_retrieval_ablation.csv"
    data.to_csv(dest, index=False)
    print(f"Written {dest}")


# ── Figure 1: Refusal precision-recall curve ──


def make_fig1():
    src = EVAL_DIR / "calibration_results.csv"
    if not src.exists():
        print(f"Skipping fig1: {src} not found")
        return
    df = pd.read_csv(src)

    fig, ax = plt.subplots(figsize=(6, 4))

    # Precision = oos_refusal_rate (true refusals / all refusals approx)
    # We plot refusal rate, FPR, FNR vs threshold
    ax.plot(df["threshold"], df["oos_refusal_rate"], "o-", label="OOS Refusal Rate (↑ better)", color="#2563eb")
    ax.plot(df["threshold"], df["false_positive_rate"], "s--", label="False Positive Rate (↓ better)", color="#dc2626")
    ax.plot(df["threshold"], df["false_negative_rate"], "^:", label="False Negative Rate (↓ better)", color="#f59e0b")

    ax.set_xlabel("Refusal Threshold (θ)", fontsize=11)
    ax.set_ylabel("Rate", fontsize=11)
    ax.set_title("Refusal Mechanism Calibration (RQ4)", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    dest = FIGURES_DIR / "fig1_refusal_curve.png"
    fig.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Written {dest}")


# ── Figure 2: Evaluation summary bar chart ──


def make_fig2():
    src = EVAL_DIR / "results_phase1.csv"
    if not src.exists():
        print(f"Skipping fig2: {src} not found")
        return
    df = pd.read_csv(src)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    colors = ["#94a3b8", "#60a5fa", "#34d399", "#a78bfa"]

    # Hallucination rate (lower is better)
    axes[0].bar(df["retriever"], df["hallucination_rate"], color=colors)
    axes[0].set_title("Hallucination Rate (↓)")
    axes[0].set_ylabel("Rate")
    axes[0].set_ylim(0, 1)

    # Citation accuracy (higher is better)
    axes[1].bar(df["retriever"], df["citation_accuracy"], color=colors)
    axes[1].set_title("Citation Accuracy (↑)")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0, 1)

    # Latency
    axes[2].bar(df["retriever"], df["mean_latency_ms"], color=colors)
    axes[2].set_title("Mean Latency")
    axes[2].set_ylabel("ms")

    fig.suptitle("Phase 1 Evaluation: 4 Retriever Conditions", fontsize=13, y=1.02)
    fig.tight_layout()

    dest = FIGURES_DIR / "fig2_evaluation_summary.png"
    fig.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Written {dest}")


def main():
    ensure_dirs()
    make_table2()
    make_table3()
    make_fig1()
    make_fig2()
    print("\nDone. Check paper/figures/")


if __name__ == "__main__":
    import json  # deferred for table3
    main()
