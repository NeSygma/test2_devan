"""
Prompt Comparison Evaluation Script
Compares PAPER_DECOMPOSITION_PROMPT, PAPER_DECOMPOSITION_PROMPT_V2, and
ONE_SHOT_CLASSIFICATION_PROMPT for solver classification accuracy and token usage.

All labels are mapped to two solvers: LP (LP+FOL) and CSP (CSP+SAT).
Uses gpt-oss-120b on Cerebras with per-prompt temperature settings.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import time
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.dataset_loader import LogicDatasetLoader
from solver_select_pipeline.prompts import (
    PAPER_DECOMPOSITION_PROMPT,
    PAPER_DECOMPOSITION_PROMPT_V2,
    ONE_SHOT_CLASSIFICATION_PROMPT,
)

# ── Label Mapping ──────────────────────────────────────────────────────────────
LABEL_MAP = {"LP": "LP", "FOL": "LP", "CSP": "CSP", "SAT": "CSP"}


def map_label(label: str) -> str:
    """Map a 4-solver label to the 2-solver scheme."""
    return LABEL_MAP.get(label.strip().upper(), "UNKNOWN")


# ── Prompt Evaluation Helpers ──────────────────────────────────────────────────

def _parse_decomposition_response(response: str) -> str:
    """Extract problem_type from a decomposition prompt JSON response."""
    try:
        if "```json" in response:
            clean = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            clean = response.split("```")[1].split("```")[0]
        else:
            clean = response
        data = json.loads(clean.strip())
        if "result" in data and len(data["result"]) > 0:
            return data["result"][0].get("problem_type", "UNKNOWN")
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        print(f"  [JSON parse error] {e}")
    return "UNKNOWN"


def _parse_oneshot_response(response: str) -> str:
    """Extract solver label from a one-shot classification response."""
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    for solver in ["LP", "FOL", "CSP", "SAT"]:
        if solver in clean:
            return solver
    return "UNKNOWN"


# Default delay between API calls (seconds) to stay under rate limits
DEFAULT_REQUEST_DELAY = 5.0


def evaluate_prompt(llm: LLMClient, prompt_template: str, prompt_name: str,
                    problems: list, is_oneshot: bool = False,
                    temperature: float = None,
                    request_delay: float = DEFAULT_REQUEST_DELAY) -> dict:
    """
    Run a single prompt strategy over all problems and return results + usage.

    Args:
        request_delay: Seconds to wait between API calls to avoid 429 errors.

    Returns dict with keys: results (list of dicts), total_usage (dict).
    """
    llm.reset_usage()
    results = []
    print(f"\n{'='*60}")
    print(f"  Evaluating: {prompt_name}")
    print(f"{'='*60}")

    for idx, problem in enumerate(tqdm(problems, desc=prompt_name)):
        # Proactive rate-limit delay (skip before the first request)
        if idx > 0 and request_delay > 0:
            time.sleep(request_delay)

        text = problem["text"]
        gold = problem["gold_mapped"]

        # Snapshot usage before
        usage_before = llm.get_total_usage()

        # Format and send prompt
        prompt = prompt_template.format(problem=text)
        try:
            response, _usage = llm.generate(
                prompt=prompt,
                system_prompt="",  # SYSTEM instruction is inside the prompt text
                temperature=temperature,
                max_completion_tokens=4096,
                max_retries=10,
            )
        except RuntimeError as e:
            # If all retries exhausted, record as error and continue
            print(f"\n  [SKIPPED] {problem['id']} - {e}")
            response = ""

        # Parse prediction
        if is_oneshot:
            raw_pred = _parse_oneshot_response(response)
        else:
            raw_pred = _parse_decomposition_response(response)
        predicted = map_label(raw_pred)

        # Token delta
        usage_after = llm.get_total_usage()
        prompt_tokens = usage_after["prompt_tokens"] - usage_before["prompt_tokens"]
        completion_tokens = usage_after["completion_tokens"] - usage_before["completion_tokens"]
        total_tokens = usage_after["total_tokens"] - usage_before["total_tokens"]

        results.append({
            "id": problem["id"],
            "gold": gold,
            "raw_prediction": raw_pred,
            "prediction": predicted,
            "match": predicted == gold,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        })

    total_usage = llm.get_total_usage()
    return {"results": results, "total_usage": total_usage}


# ── Plotting ───────────────────────────────────────────────────────────────────

def generate_plots(summary: dict, output_dir: str = "media"):
    """
    Generate comparison plots for accuracy and token usage.
    summary: {prompt_name: {"accuracy": float, "total_usage": dict, ...}}
    """
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)

    names = list(summary.keys())
    accuracies = [summary[n]["accuracy"] for n in names]
    prompt_tokens = [summary[n]["total_usage"]["prompt_tokens"] for n in names]
    completion_tokens = [summary[n]["total_usage"]["completion_tokens"] for n in names]

    # Short display labels
    short_names = []
    for n in names:
        if "V2" in n:
            short_names.append("Decomposition V2\n(2-solver)")
        elif "DECOMPOSITION" in n.upper():
            short_names.append("Decomposition V1\n(4-solver)")
        else:
            short_names.append("One-Shot\nClassification")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ── 1. Accuracy Bar Chart ────────────────────────────────────────────────
    colors_acc = ["#4C72B0", "#55A868", "#C44E52"]
    bars = axes[0].bar(short_names, accuracies, color=colors_acc, edgecolor="white",
                       linewidth=0.8, width=0.55)
    axes[0].set_ylim(0, 1.15)
    axes[0].set_ylabel("Accuracy", fontsize=12)
    axes[0].set_title("Classification Accuracy (2-solver: LP / CSP)", fontsize=13, fontweight="bold")
    for bar, acc in zip(bars, accuracies):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                     f"{acc:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    # ── 2. Token Usage Stacked Bar Chart ─────────────────────────────────────
    x = np.arange(len(names))
    width = 0.55
    bars_p = axes[1].bar(x, prompt_tokens, width, label="Prompt Tokens",
                         color="#4C72B0", edgecolor="white", linewidth=0.8)
    bars_c = axes[1].bar(x, completion_tokens, width, bottom=prompt_tokens,
                         label="Completion Tokens", color="#DD8452",
                         edgecolor="white", linewidth=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(short_names, fontsize=10)
    axes[1].set_ylabel("Token Count", fontsize=12)
    axes[1].set_title("Total Token Usage by Prompt Strategy", fontsize=13, fontweight="bold")
    axes[1].legend(loc="upper right")

    # Annotate totals on top
    for i in range(len(names)):
        total = prompt_tokens[i] + completion_tokens[i]
        axes[1].text(i, total + max(prompt_tokens) * 0.02, f"{total:,}",
                     ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "prompt_comparison_results.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {plot_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare prompt strategies for 2-solver classification (LP / CSP)."
    )
    parser.add_argument("--limit", type=int, default=5,
                        help="Number of problems per dataset (default: 5)")
    parser.add_argument("--out", type=str, default="prompt_comparison_results.csv",
                        help="Output CSV filename")
    args = parser.parse_args()

    # Load mixed dataset
    print("Loading mixed datasets...")
    problems = LogicDatasetLoader.load_mixed_datasets(limit_per_dataset=args.limit)
    print(f"Loaded {len(problems)} problems.")

    # Map gold labels to 2-solver scheme
    for p in problems:
        p["gold_mapped"] = map_label(p.get("gold_solver", "UNKNOWN"))

    # Print dataset distribution
    gold_counts = pd.Series([p["gold_mapped"] for p in problems]).value_counts()
    print(f"\nGold label distribution (2-solver):\n{gold_counts.to_string()}\n")

    # Define prompt strategies to evaluate
    # Each tuple: (name, template, is_oneshot, temperature)
    #   - V1: temperature=0
    #   - V2: temperature=0.01
    #   - One-shot: temperature=None (API default)
    strategies = [
        ("PAPER_DECOMPOSITION_PROMPT",    PAPER_DECOMPOSITION_PROMPT,    False, 0),
        ("PAPER_DECOMPOSITION_PROMPT_V2", PAPER_DECOMPOSITION_PROMPT_V2, False, 0.01),
        ("ONE_SHOT_CLASSIFICATION",       ONE_SHOT_CLASSIFICATION_PROMPT, True,  None),
    ]

    # Use a shared LLM client (gpt-oss-120b, resets usage per strategy)
    llm = LLMClient(model="gpt-oss-120b")

    all_rows = []
    summary = {}

    for strat_idx, (name, template, is_oneshot, temp) in enumerate(strategies):
        # Cooldown between strategies to let the rate limit bucket refill
        if strat_idx > 0:
            print("\n  [Cooldown 5s between strategies...]")
            time.sleep(5)

        temp_str = f"temp={temp}" if temp is not None else "temp=default"
        print(f"  [{temp_str}]")
        result = evaluate_prompt(llm, template, name, problems, is_oneshot=is_oneshot, temperature=temp)

        # Compute accuracy
        df_strat = pd.DataFrame(result["results"])
        accuracy = df_strat["match"].mean()

        summary[name] = {
            "accuracy": accuracy,
            "total_usage": result["total_usage"],
        }

        # Tag rows for the combined CSV
        for row in result["results"]:
            row["prompt_strategy"] = name
        all_rows.extend(result["results"])

        print(f"  -> {name}: Accuracy = {accuracy:.2%}  |  "
              f"Tokens = {result['total_usage']['total_tokens']:,}")

    # Save combined CSV
    df_all = pd.DataFrame(all_rows)
    df_all.to_csv(args.out, index=False)
    print(f"\nResults saved to {args.out}")

    # Print summary table
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    for name, info in summary.items():
        print(f"  {name:40s}  Acc={info['accuracy']:.2%}  "
              f"Tokens={info['total_usage']['total_tokens']:,}")
    print(f"{'='*60}")

    # Generate plots
    try:
        generate_plots(summary)
    except ImportError:
        print("\nmatplotlib not installed — skipping plots.")


if __name__ == "__main__":
    main()
