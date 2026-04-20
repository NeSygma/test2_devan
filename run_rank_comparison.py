"""
Rank Prompt Comparison Evaluation Script
Compares ADAPTIVE_SELECTION_PROMPT_RANK, RANK_2, RANK_3, and RANK_4
for solver ranking quality using order-based scoring.

Scoring evaluates the FULL ranking order against the ideal per benchmark:
  - aspbench (easy/hard): ideal = [CLINGO, Z3, VAMPIRE]
  - ar_lsat:              ideal = [Z3, CLINGO, VAMPIRE]
  - folio:                ideal = [VAMPIRE, Z3, CLINGO]

Scoring rules:
  - 1.0  : Ranking matches the ideal order exactly
  - 0.75 : 1st and 2nd solvers are swapped, but worst solver is still last
  - 0.5  : 1st solver is correct, but 2nd and 3rd solvers are swapped
  - 0.0  : The worst solver (3rd in ideal) appears in 1st or 2nd place

Evaluates on FOLIO, ARLSAT, and ASPBench (easy + hard) datasets.
Runs each prompt on TWO LLMs:
  - openai/gpt-oss-120b  (Nvidia NIM)
  - gemini-3.1-flash-lite-preview  (Google AI Studio)
Results are separated per LLM under results_rank/{llm_name}/.
Outputs structured results to results_rank/ directory.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import time
import datetime
import random
from string import Template
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.dataset_loader import LogicDatasetLoader
from solver_select_pipeline.prompts import (
    ADAPTIVE_SELECTION_PROMPT_RANK,
    ADAPTIVE_SELECTION_PROMPT_RANK_2,
    ADAPTIVE_SELECTION_PROMPT_RANK_2_1,
    ADAPTIVE_SELECTION_PROMPT_RANK_3,
    ADAPTIVE_SELECTION_PROMPT_RANK_4,
)

# ── Label Mapping ──────────────────────────────────────────────────────────────
# Gold labels (dataset): SAT → CSP, everything else stays
GOLD_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}

# ADAPTIVE_SELECTION_PROMPT_RANK outputs CLINGO/VAMPIRE/Z3 → map to LP/FOL/CSP
RANK_LABEL_MAP = {"CLINGO": "LP", "VAMPIRE": "FOL", "Z3": "CSP"}

# ── Per-Benchmark Ideal Rankings ───────────────────────────────────────────────
# The ideal solver ranking order for each benchmark.
# Scoring: 1.0 if exact match, 0.75 if top-2 swapped (worst still last),
#          0.5 if 1st correct but 2nd/3rd swapped, 0.0 otherwise.
BENCHMARK_IDEAL_RANKINGS = {
    "aspbench_easy": ["CLINGO", "Z3", "VAMPIRE"],
    "aspbench_hard": ["CLINGO", "Z3", "VAMPIRE"],
    "ar_lsat":       ["Z3", "CLINGO", "VAMPIRE"],
    "folio":         ["VAMPIRE", "Z3", "CLINGO"],
}

# ── LLM Configurations ────────────────────────────────────────────────────────
LLM_CONFIGS = [
    {
        "model": "openai/gpt-oss-120b",
        "short_name": "gpt_oss_120b",
        "display_name": "GPT-OSS-120B",
    },
    {
        "model": "gemini-3.1-flash-lite-preview",
        "short_name": "gemini_31_flash_lite",
        "display_name": "Gemini 3.1 Flash Lite",
    },
]


def map_label(label: str, label_map: dict = None) -> str:
    """Map a solver label using the given label map (3-solver scheme)."""
    if label_map is None:
        label_map = GOLD_LABEL_MAP
    return label_map.get(label.strip().upper(), "UNKNOWN")


# ── Prompt Evaluation Helpers ──────────────────────────────────────────────────

def _parse_full_ranking(response: str) -> list:
    """Extract the full solver ranking list from response JSON.
    
    Returns a list of solver names (e.g. ['CLINGO', 'Z3', 'VAMPIRE']),
    or an empty list on parse failure.
    """
    if not response:
        return []
    # Try JSON extraction
    try:
        if "```json" in response:
            clean = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            clean = response.split("```")[1].split("```")[0]
        else:
            clean = response
        data = json.loads(clean.strip())
        ranking = data.get("solver_ranking", [])
        if ranking and len(ranking) > 0:
            # Normalize to uppercase
            normalized = [s.strip().upper() for s in ranking]
            # Validate all entries are known solvers
            valid_solvers = {"VAMPIRE", "CLINGO", "Z3"}
            if all(s in valid_solvers for s in normalized):
                return normalized
    except (json.JSONDecodeError, AttributeError, IndexError):
        pass
    return []


def _get_top_solver(ranking: list) -> str:
    """Get the top-ranked solver from a full ranking, or UNKNOWN."""
    if ranking and len(ranking) > 0:
        return ranking[0]
    return "UNKNOWN"


def _determine_rank_match_type(ranking: list, benchmark: str) -> str:
    """Determine the rank match category for the model's ranking.

    Compares the model's ranking to the ideal ranking for the benchmark:
      - "perfect"  : Exact match with ideal order
      - "top2swap" : 1st and 2nd solvers swapped, worst solver still in last place
      - "bot2swap" : 1st solver is correct, but 2nd and 3rd solvers are swapped
      - "bad"      : Worst solver (3rd in ideal) appears in 1st or 2nd place,
                     or ranking is empty/invalid
    """
    ideal = BENCHMARK_IDEAL_RANKINGS.get(benchmark)
    if not ideal or not ranking or len(ranking) < 3:
        return "bad"

    model_top3 = ranking[:3]
    worst_solver = ideal[2]  # the solver that should be ranked last

    # If the worst solver leaked into position 1 or 2 → bad
    if worst_solver in model_top3[:2]:
        return "bad"

    # Exact match with ideal order
    if model_top3 == ideal:
        return "perfect"

    # 1st and 2nd swapped, worst solver still last
    if model_top3[0] == ideal[1] and model_top3[1] == ideal[0] and model_top3[2] == ideal[2]:
        return "top2swap"

    # 1st correct, but 2nd and 3rd swapped
    if model_top3[0] == ideal[0] and model_top3[1] == ideal[2] and model_top3[2] == ideal[1]:
        return "bot2swap"

    return "bad"


def _format_adaptive_prompt(prompt_template: str, problem_text: str) -> str:
    """Format the ADAPTIVE_SELECTION_PROMPT using the problem text."""
    return Template(prompt_template).safe_substitute(
        context=problem_text,
        question="(see context above)",
        options="(see context above)",
    )


# Default delay between API calls (seconds) to stay under rate limits
DEFAULT_REQUEST_DELAY = 5.0


def _infer_benchmark(problem_id: str) -> str:
    """Infer benchmark name from a problem ID prefix."""
    if problem_id.startswith("folio"):
        return "folio"
    if problem_id.startswith("arlsat"):
        return "ar_lsat"
    if problem_id.startswith("aspbench_easy"):
        return "aspbench_easy"
    if problem_id.startswith("aspbench_hard"):
        return "aspbench_hard"
    return "unknown"


def load_rank_datasets(limit_per_dataset: int = 5):
    """
    Load only FOLIO, AR-LSAT, and ASPBench (easy + hard) datasets
    for rank prompt comparison.
    """
    all_records = []
    all_records.extend(LogicDatasetLoader.load_folio_huggingface(limit_per_dataset))
    all_records.extend(LogicDatasetLoader.load_ar_lsat(limit_per_dataset))
    all_records.extend(LogicDatasetLoader.load_aspbench("easy", limit_per_dataset))
    all_records.extend(LogicDatasetLoader.load_aspbench("hard", limit_per_dataset))

    # Shuffle to test the pipeline's robustness
    random.shuffle(all_records)
    return all_records


def evaluate_prompt(llm: LLMClient, prompt_template: str, prompt_name: str,
                    problems: list, label_map: dict = None,
                    temperature: float = None,
                    request_delay: float = DEFAULT_REQUEST_DELAY) -> dict:
    """
    Run a single prompt strategy over all problems and return results + usage.

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
        benchmark = _infer_benchmark(problem["id"])

        # Snapshot usage before
        usage_before = llm.get_total_usage()

        # Format prompt
        prompt = _format_adaptive_prompt(prompt_template, text)

        reasoning_trace = ""
        try:
            response, _usage, reasoning_trace = llm.generate(
                prompt=prompt,
                system_prompt="",  # SYSTEM instruction is inside the prompt text
                temperature=temperature,
                max_completion_tokens=4096,
                max_retries=10,
                reasoning_format="parsed",
            )
        except RuntimeError as e:
            # If all retries exhausted, record as error and continue
            print(f"\n  [SKIPPED] {problem['id']} - {e}")
            response = ""

        # Parse FULL ranking
        full_ranking = _parse_full_ranking(response)
        raw_pred = _get_top_solver(full_ranking)
        predicted = map_label(raw_pred, label_map)

        # Compute ranking match type
        rank_match_type = _determine_rank_match_type(full_ranking, benchmark)

        # Token delta
        usage_after = llm.get_total_usage()
        prompt_tokens = usage_after["prompt_tokens"] - usage_before["prompt_tokens"]
        completion_tokens = usage_after["completion_tokens"] - usage_before["completion_tokens"]
        total_tokens = usage_after["total_tokens"] - usage_before["total_tokens"]

        results.append({
            "id": problem["id"],
            "benchmark": benchmark,
            "gold": gold,
            "raw_prediction": raw_pred,
            "prediction": predicted,
            "match": predicted == gold,
            # Full ranking data
            "full_ranking": full_ranking,
            "ideal_ranking": BENCHMARK_IDEAL_RANKINGS.get(benchmark, []),
            "rank_match_type": rank_match_type,
            # Token usage
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            # Detailed trace columns
            "full_prompt": prompt,
            "problem_text": text,
            "raw_response": response,
            "reasoning_trace": reasoning_trace if reasoning_trace else response,
        })

    total_usage = llm.get_total_usage()
    return {"results": results, "total_usage": total_usage}


# ── Short Display Names ───────────────────────────────────────────────────────

def _get_short_name(name: str) -> str:
    """Map prompt strategy name to a short display label."""
    upper = name.upper()
    if "RANK_4" in upper:
        return "Adaptive\nRank V4"
    if "RANK_3" in upper:
        return "Adaptive\nRank V3"
    if "RANK_2_1" in upper:
        return "Adaptive\nRank V2.1"
    if "RANK_2" in upper:
        return "Adaptive\nRank V2"
    if "RANK" in upper:
        return "Adaptive\nRank V1"
    return name


# ── Plotting ───────────────────────────────────────────────────────────────────

def generate_plots(summary: dict, llm_display_name: str,
                   output_dir: str = "results_rank/media"):
    """
    Generate comparison plots for rank order scores, accuracy, and token usage
    for a single LLM's evaluation results.
    summary: {prompt_name: {"rank_order_score": float, "accuracy": float, "total_usage": dict, ...}}
    """
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)

    names = list(summary.keys())
    short_names = [_get_short_name(n) for n in names]

    benchmarks = list(BENCHMARK_IDEAL_RANKINGS.keys())
    bench_short = {
        "aspbench_easy": "ASPBench\nEasy",
        "aspbench_hard": "ASPBench\nHard",
        "ar_lsat": "AR-LSAT",
        "folio": "FOLIO",
    }

    colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B3"][:len(names)]
    x = np.arange(len(benchmarks))
    n_strats = len(names)
    width = 0.8 / n_strats

    # ── Figure 1: Total Token Usage ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle(f"Total Token Usage — {llm_display_name}",
                 fontsize=15, fontweight="bold", y=1.02)

    prompt_tokens = [summary[n]["total_usage"]["prompt_tokens"] for n in names]
    completion_tokens = [summary[n]["total_usage"]["completion_tokens"] for n in names]
    x2 = np.arange(len(names))
    
    ax.bar(x2, prompt_tokens, 0.35, label="Prompt Tokens",
           color="#4C72B0", edgecolor="white", linewidth=0.8)
    ax.bar(x2, completion_tokens, 0.35, bottom=prompt_tokens,
           label="Completion Tokens", color="#DD8452",
           edgecolor="white", linewidth=0.8)
    
    ax.set_xticks(x2)
    ax.set_xticklabels(short_names, fontsize=10)
    ax.set_ylabel("Token Count", fontsize=12)
    ax.set_title("Prompt vs Completion Tokens", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right")
    
    for i in range(len(names)):
        total = prompt_tokens[i] + completion_tokens[i]
        ax.text(i, total + max(prompt_tokens) * 0.02, f"{total:,}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "rank_token_usage.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nPlot saved to {plot_path}")

    # ── Figure 2: Score Distribution (perfect / partial / bot2swap / zero) ────
    fig, axes = plt.subplots(1, len(names), figsize=(7 * len(names), 6))
    fig.suptitle(f"Score Distribution — {llm_display_name}",
                 fontsize=15, fontweight="bold", y=1.02)
    if len(names) == 1:
        axes = [axes]

    for i, name in enumerate(names):
        per_bench = summary[name].get("per_benchmark", {})
        categories = ["1.0\n(Perfect)", "0.75\n(Top-2 Swap)", "0.5\n(Bot-2 Swap)", "0.0\n(Bad)"]
        for j, bench in enumerate(benchmarks):
            stats = per_bench.get(bench, {})
            pct_perfect = stats.get("pct_perfect", 0)
            pct_top2swap = stats.get("pct_top2swap", 0)
            pct_bot2swap = stats.get("pct_bot2swap", 0)
            pct_bad = stats.get("pct_bad", 0)
            vals = [pct_perfect, pct_top2swap, pct_bot2swap, pct_bad]
            x_pos = np.arange(len(categories)) + j * 0.18
            axes[i].bar(x_pos, vals, 0.16, label=bench_short.get(bench, bench).replace("\n", " "),
                        edgecolor="white", linewidth=0.5)

        axes[i].set_xticks(np.arange(len(categories)) + 0.27)
        axes[i].set_xticklabels(categories, fontsize=10)
        axes[i].set_ylim(0, 105)
        axes[i].set_ylabel("% of Problems", fontsize=12)
        axes[i].set_title(f"{short_names[i].replace(chr(10), ' ')}\nScore Distribution",
                          fontsize=13, fontweight="bold")
        axes[i].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "rank_score_distribution.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {plot_path}")

    # ── Figure 3: Top-1 Accuracy (Overall + Per-Benchmark) ───────────────────
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"Top-1 Accuracy — {llm_display_name}",
                 fontsize=15, fontweight="bold", y=1.02)

    # 3a. Overall accuracy
    overall_acc = [summary[n]["accuracy"] for n in names]
    bars = axes[0].bar(short_names, [a * 100 for a in overall_acc], color=colors,
                       edgecolor="white", linewidth=0.8, width=0.35)
    axes[0].set_ylim(0, 115)
    axes[0].set_ylabel("Accuracy (%)", fontsize=12)
    axes[0].set_title("Overall Top-1 Accuracy", fontsize=13, fontweight="bold")
    for bar, acc in zip(bars, overall_acc):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"{acc:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    # 3b. Per-benchmark accuracy grouped bar chart
    for i, name in enumerate(names):
        per_bench = summary[name].get("per_benchmark", {})
        bench_accs = [per_bench.get(b, {}).get("accuracy", 0.0) * 100 for b in benchmarks]
        bars = axes[1].bar(x + i * width - (n_strats - 1) * width / 2, bench_accs, width,
                           label=short_names[i].replace("\n", " "),
                           color=colors[i], edgecolor="white", linewidth=0.8)
        for bar, acc in zip(bars, bench_accs):
            axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         f"{acc:.0f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")

    axes[1].set_xticks(x)
    axes[1].set_xticklabels([bench_short.get(b, b) for b in benchmarks], fontsize=10)
    axes[1].set_ylim(0, 115)
    axes[1].set_ylabel("Accuracy (%)", fontsize=12)
    axes[1].set_title("Top-1 Accuracy by Benchmark", fontsize=13, fontweight="bold")
    axes[1].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "rank_accuracy_comparison.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {plot_path}")

    # ── Figure 4: Per-Benchmark Token Usage ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle(f"Per-Benchmark Token Usage — {llm_display_name}",
                 fontsize=15, fontweight="bold", y=1.02)

    for i, name in enumerate(names):
        per_bench = summary[name].get("per_benchmark", {})
        bench_tokens = [per_bench.get(b, {}).get("total_tokens", 0) for b in benchmarks]
        bars = ax.bar(x + i * width - (n_strats - 1) * width / 2, bench_tokens, width,
                      label=short_names[i].replace("\n", " "),
                      color=colors[i], edgecolor="white", linewidth=0.8)
        for bar, tok in zip(bars, bench_tokens):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(bench_tokens) * 0.01,
                    f"{tok:,}", ha="center", va="bottom", fontsize=7, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([bench_short.get(b, b) for b in benchmarks], fontsize=10)
    ax.set_ylabel("Total Tokens", fontsize=12)
    ax.set_title("Token Usage by Benchmark", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "rank_token_per_benchmark.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {plot_path}")


# ── Result Saving ──────────────────────────────────────────────────────────────

def save_structured_results(prompt_name: str, results: list, total_usage: dict,
                            accuracy: float,
                            per_benchmark_stats: dict,
                            llm_model: str, temperature: float,
                            output_root: str = "results_rank"):
    """
    Save results in a structured folder layout:
        results_rank/{llm_short_name}/{prompt_name}/{benchmark_name}/results.jsonl
        results_rank/{llm_short_name}/{prompt_name}/summary.json
    """
    prompt_dir = os.path.join(output_root, prompt_name)
    os.makedirs(prompt_dir, exist_ok=True)

    # Group results by benchmark
    benchmarks: dict[str, list] = {}
    for row in results:
        bench = row.get("benchmark", "unknown")
        benchmarks.setdefault(bench, []).append(row)

    # Write per-benchmark JSONL files
    for bench_name, rows in benchmarks.items():
        bench_dir = os.path.join(prompt_dir, bench_name)
        os.makedirs(bench_dir, exist_ok=True)
        jsonl_path = os.path.join(bench_dir, "results.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Write summary JSON
    summary_data = {
        "prompt_name": prompt_name,
        "llm_model": llm_model,
        "temperature": temperature,
        "timestamp": datetime.datetime.now().isoformat(),
        "num_problems": len(results),
        "top1_accuracy": accuracy,
        "total_usage": total_usage,
        "per_benchmark": per_benchmark_stats,
        "scoring_rubric": {
            "description": "Categories: perfect, top2swap, bot2swap, bad",
            "ideal_rankings": {k: v for k, v in BENCHMARK_IDEAL_RANKINGS.items()},
        },
    }
    summary_path = os.path.join(prompt_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    print(f"  Results saved to {prompt_dir}/")


# ── Per-LLM Evaluation ────────────────────────────────────────────────────────

def compute_per_benchmark_stats(df_strat: pd.DataFrame) -> dict:
    """Compute per-benchmark breakdown statistics from a strategy DataFrame."""
    per_bench_scores = {}
    for bench_name, bench_df in df_strat.groupby("benchmark"):
        total = len(bench_df)
        num_perfect = (bench_df["rank_match_type"] == "perfect").sum()
        num_top2swap = (bench_df["rank_match_type"] == "top2swap").sum()
        num_bot2swap = (bench_df["rank_match_type"] == "bot2swap").sum()
        num_bad = (bench_df["rank_match_type"] == "bad").sum()
        per_bench_scores[bench_name] = {
            "num_problems": total,
            "num_perfect": int(num_perfect),
            "num_top2swap": int(num_top2swap),
            "num_bot2swap": int(num_bot2swap),
            "num_bad": int(num_bad),
            "pct_perfect": num_perfect / total * 100 if total > 0 else 0.0,
            "pct_top2swap": num_top2swap / total * 100 if total > 0 else 0.0,
            "pct_bot2swap": num_bot2swap / total * 100 if total > 0 else 0.0,
            "pct_bad": num_bad / total * 100 if total > 0 else 0.0,
            "accuracy": bench_df["match"].mean(),
            "total_tokens": int(bench_df["total_tokens"].sum()),
        }
    return per_bench_scores


def run_llm_evaluation(llm_config: dict, strategies: list, problems: list,
                       output_root: str) -> dict:
    """
    Run all prompt strategies on a single LLM and return summary dict.
    Results are saved under output_root/{llm_short_name}/.
    """
    model_name = llm_config["model"]
    short_name = llm_config["short_name"]
    display_name = llm_config["display_name"]
    llm_out = os.path.join(output_root, short_name)

    print(f"\n{'#'*80}")
    print(f"  LLM: {display_name}  ({model_name})")
    print(f"{'#'*80}")

    llm = LLMClient(model=model_name)
    summary = {}

    for strat_idx, (name, template, lmap, temp) in enumerate(strategies):
        # Cooldown between strategies to let the rate limit bucket refill
        if strat_idx > 0:
            print("\n  [Cooldown 5s between strategies...]")
            time.sleep(5)

        print(f"  [temp={temp}]")
        result = evaluate_prompt(llm, template, name, problems,
                                 label_map=lmap, temperature=temp)

        # Compute scores
        df_strat = pd.DataFrame(result["results"])
        accuracy = df_strat["match"].mean()

        # Per-benchmark breakdown
        per_bench_scores = compute_per_benchmark_stats(df_strat)

        summary[name] = {
            "accuracy": accuracy,
            "total_usage": result["total_usage"],
            "per_benchmark": per_bench_scores,
        }

        # Save structured results to folders (per-LLM subdirectory)
        save_structured_results(
            prompt_name=name,
            results=result["results"],
            total_usage=result["total_usage"],
            accuracy=accuracy,
            per_benchmark_stats=per_bench_scores,
            llm_model=model_name,
            temperature=temp,
            output_root=llm_out,
        )

        print(f"\n  -> {name}:")
        print(f"     Top-1 Accuracy = {accuracy:.2%}  |  "
              f"Tokens = {result['total_usage']['total_tokens']:,}")
        # Per-benchmark breakdown
        for bench_name in sorted(per_bench_scores.keys()):
            bs = per_bench_scores[bench_name]
            print(f"       {bench_name:15s}: "
                  f"(Perfect={bs['num_perfect']}, Top2Swap={bs['num_top2swap']}, Bot2Swap={bs['num_bot2swap']}, Bad={bs['num_bad']})  "
                  f"Acc={bs['accuracy']:.2%}")

    # Print per-LLM summary table
    print(f"\n{'='*80}")
    print(f"  SUMMARY — {display_name}")
    print(f"{'='*80}")
    print(f"  {'Prompt':<45s}  {'Acc':>6s}  {'Tokens':>10s}")
    print(f"  {'-'*45}  {'-'*6}  {'-'*10}")
    for name, info in summary.items():
        print(f"  {name:<45s}  {info['accuracy']:>5.1%}  "
              f"{info['total_usage']['total_tokens']:>10,}")
    print(f"{'='*80}")

    # Generate per-LLM plots
    try:
        media_dir = os.path.join(llm_out, "media")
        generate_plots(summary, llm_display_name=display_name, output_dir=media_dir)
    except ImportError:
        print("\nmatplotlib not installed — skipping plots.")

    return summary


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare ADAPTIVE_SELECTION_PROMPT_RANK, RANK_2, RANK_3, and RANK_4 "
                    "for solver ranking quality using weighted scoring. "
                    "Evaluates on FOLIO, AR-LSAT, and ASPBench datasets "
                    "across multiple LLMs (GPT-OSS-120B and Gemini 3.1 Flash Lite)."
    )
    parser.add_argument("--limit", type=int, default=5,
                        help="Number of problems per dataset (default: 5)")
    parser.add_argument("--out", type=str, default="results_rank",
                        help="Output root directory (default: results_rank)")
    args = parser.parse_args()

    # Load datasets (FOLIO, AR-LSAT, ASPBench easy + hard only)
    print("Loading datasets (FOLIO, AR-LSAT, ASPBench)...")
    problems = load_rank_datasets(limit_per_dataset=args.limit)
    print(f"Loaded {len(problems)} problems.")

    # Map gold labels to 3-solver scheme (SAT -> CSP)
    for p in problems:
        p["gold_mapped"] = map_label(p.get("gold_solver", "UNKNOWN"), GOLD_LABEL_MAP)

    # Print dataset distribution
    gold_counts = pd.Series([p["gold_mapped"] for p in problems]).value_counts()
    print(f"\nGold label distribution (3-solver):\n{gold_counts.to_string()}\n")

    # Print scoring rubric
    print("Scoring rubric:")
    print("  perfect  = exact ideal order")
    print("  top2swap = top-2 swapped, worst solver still last")
    print("  bot2swap = 1st correct, but 2nd and 3rd swapped")
    print("  bad      = worst solver in position 1 or 2")
    print("\nIdeal rankings per benchmark:")
    for bench, ideal in BENCHMARK_IDEAL_RANKINGS.items():
        print(f"  {bench:15s}: {' > '.join(ideal)}")
    print()

    # Define prompt strategies to evaluate
    strategies = [
        ("ADAPTIVE_SELECTION_PROMPT_RANK", ADAPTIVE_SELECTION_PROMPT_RANK, RANK_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_RANK_2", ADAPTIVE_SELECTION_PROMPT_RANK_2, RANK_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_RANK_2_1", ADAPTIVE_SELECTION_PROMPT_RANK_2_1, RANK_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_RANK_3", ADAPTIVE_SELECTION_PROMPT_RANK_3, RANK_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_RANK_4", ADAPTIVE_SELECTION_PROMPT_RANK_4, RANK_LABEL_MAP, 0),
    ]

    # Run evaluation on each LLM
    all_llm_summaries = {}
    for llm_idx, llm_config in enumerate(LLM_CONFIGS):
        # Cooldown between LLMs
        if llm_idx > 0:
            print("\n\n  [Cooldown 10s between LLMs...]")
            time.sleep(10)

        llm_summary = run_llm_evaluation(
            llm_config=llm_config,
            strategies=strategies,
            problems=problems,
            output_root=args.out,
        )
        all_llm_summaries[llm_config["display_name"]] = llm_summary

    # Final cross-LLM summary
    print(f"\n\n{'#'*80}")
    print(f"  FINAL CROSS-LLM SUMMARY")
    print(f"{'#'*80}")
    print(f"  {'LLM':<25s}  {'Prompt':<40s}  {'Acc':>6s}  {'Tokens':>10s}")
    print(f"  {'-'*25}  {'-'*40}  {'-'*6}  {'-'*10}")
    for llm_name, llm_summary in all_llm_summaries.items():
        for prompt_name, info in llm_summary.items():
            print(f"  {llm_name:<25s}  {prompt_name:<40s}  "
                  f"{info['accuracy']:>5.1%}  {info['total_usage']['total_tokens']:>10,}")
    print(f"{'#'*80}")


if __name__ == "__main__":
    main()
