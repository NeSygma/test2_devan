"""
Prompt Comparison Evaluation Script
Compares PAPER_DECOMPOSITION_PROMPT vs ADAPTIVE_SELECTION_PROMPT
for solver classification accuracy and token usage.
All labels are mapped to three solvers: LP, FOL, and CSP.
- PAPER_DECOMPOSITION_PROMPT: LP→LP, FOL→FOL, CSP→CSP, SAT→CSP
- ADAPTIVE_SELECTION_PROMPT: LP→LP, FOL→FOL, SAT→CSP
Uses openai/gpt-oss-120b on Nvidia NIM with temperature=0 for both prompts.
Outputs a detailed CSV with full prompt, problem, output, and reasoning trace.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import time
from string import Template
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.dataset_loader import LogicDatasetLoader
from solver_select_pipeline.prompts import (
    PAPER_DECOMPOSITION_PROMPT,
    PAPER_DECOMPOSITION_PROMPT_V2,
    PAPER_DECOMPOSITION_PROMPT_V3,
    ADAPTIVE_SELECTION_PROMPT,
    ADAPTIVE_SELECTION_PROMPT_V2,
    ADAPTIVE_SELECTION_PROMPT_V2_1,
    ADAPTIVE_SELECTION_PROMPT_V3,
    ADAPTIVE_SELECTION_PROMPT_V3_1,
    ONE_SHOT_CLASSIFICATION_PROMPT,
    FEW_SHOT_CLASSIFICATION_PROMPT,
)

# ── Label Mapping ──────────────────────────────────────────────────────────────
# Gold labels (dataset): SAT → CSP, everything else stays
GOLD_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}

# Per-prompt prediction maps (3-solver: LP / FOL / CSP)
# PAPER_DECOMPOSITION outputs LP/FOL/CSP/SAT → map SAT to CSP
DECOMPOSITION_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}
# PAPER_DECOMPOSITION_V2 outputs LP, FOL, CSP/SAT/SMT → map CSP/SAT/SMT to CSP
DECOMPOSITION_V2_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP/SAT/SMT": "CSP"}
# ADAPTIVE_SELECTION outputs FOL/LP/SAT → map SAT to CSP
ADAPTIVE_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "SAT": "CSP"}
# FEW_SHOT_CLASSIFICATION outputs LP/FOL/CSP → direct map
FEW_SHOT_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP"}
# ONE_SHOT_CLASSIFICATION outputs LP/FOL/CSP/SAT → map SAT to CSP
ONE_SHOT_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}
# PAPER_DECOMPOSITION_V3 outputs LP, FOL, SAT → map SAT to CSP
DECOMPOSITION_V3_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "SAT": "CSP"}


def map_label(label: str, label_map: dict = None) -> str:
    """Map a solver label using the given label map (3-solver scheme)."""
    if label_map is None:
        label_map = GOLD_LABEL_MAP
    return label_map.get(label.strip().upper(), "UNKNOWN")


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


def _parse_adaptive_response(response: str) -> str:
    """Extract solver label from ADAPTIVE_SELECTION_PROMPT response (FOL/LP/SAT)."""
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    # Check in order of specificity
    for solver in ["FOL", "LP", "SAT"]:
        if solver in clean:
            return solver
    return "UNKNOWN"


def _parse_adaptive_v2_response(response: str) -> str:
    """Extract solver label from ADAPTIVE_SELECTION_PROMPT_V2 json response."""
    try:
        if "```json" in response:
            clean = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            clean = response.split("```")[1].split("```")[0]
        else:
            clean = response
        data = json.loads(clean.strip())
        return data.get("problem_type", "UNKNOWN")
    except Exception:
        pass
    return "UNKNOWN"


def _parse_adaptive_v3_response(response: str) -> str:
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    prefix = "CHOSEN SYMBOLIC LANGUANGE"
    if prefix in clean:
        after_prefix = clean.split(prefix)[-1]
        for solver in ["FOL", "LP", "SAT"]:
            if solver in after_prefix:
                return solver
    # Fallback broadly just in case the model dropped the prefix
    for solver in ["FOL", "LP", "SAT"]:
        if solver in clean:
            return solver
    return "UNKNOWN"


def _parse_few_shot_response(response: str) -> str:
    """Extract solver label from classification prompt response (LP/FOL/CSP/SAT)."""
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    for solver in ["FOL", "CSP", "LP", "SAT"]:
        if solver in clean:
            return solver
    return "UNKNOWN"


def _format_adaptive_prompt(prompt_template: str, problem_text: str) -> str:
    """Format the ADAPTIVE_SELECTION_PROMPT using the problem text."""
    return Template(prompt_template).safe_substitute(
        context=problem_text,
        question="(see context above)",
        options="(see context above)",
    )


# Default delay between API calls (seconds) to stay under rate limits
DEFAULT_REQUEST_DELAY = 5.0


def evaluate_prompt(llm: LLMClient, prompt_template: str, prompt_name: str,
                    problems: list, parser: str = "decomposition",
                    label_map: dict = None,
                    temperature: float = None,
                    request_delay: float = DEFAULT_REQUEST_DELAY) -> dict:
    """
    Run a single prompt strategy over all problems and return results + usage.

    Args:
        parser: 'decomposition' or 'adaptive' — determines how to parse the response.
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

        # Format prompt based on strategy type
        if parser.startswith("adaptive"):
            prompt = _format_adaptive_prompt(prompt_template, text)
        else:
            prompt = prompt_template.format(problem=text)

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

        # Parse prediction
        if parser == "adaptive":
            raw_pred = _parse_adaptive_response(response)
        elif parser == "adaptive_v2":
            raw_pred = _parse_adaptive_v2_response(response)
        elif parser == "adaptive_v3":
            raw_pred = _parse_adaptive_v3_response(response)
        elif parser in ("few_shot", "one_shot"):
            raw_pred = _parse_few_shot_response(response)
        else:
            raw_pred = _parse_decomposition_response(response)
        predicted = map_label(raw_pred, label_map)

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
            # Detailed trace columns
            "full_prompt": prompt,
            "problem_text": text,
            "raw_response": response,
            "reasoning_trace": reasoning_trace if reasoning_trace else response,
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
        if "ADAPTIVE" in n.upper() and "V3_1" in n.upper():
            short_names.append("Adaptive\nSelection V3.1")
        elif "ADAPTIVE" in n.upper() and "V3" in n.upper():
            short_names.append("Adaptive\nSelection V3")
        elif "ADAPTIVE" in n.upper() and "V2_1" in n.upper():
            short_names.append("Adaptive\nSelection V2.1")
        elif "ADAPTIVE" in n.upper() and "V2" in n.upper():
            short_names.append("Adaptive\nSelection V2")
        elif "ADAPTIVE" in n.upper():
            short_names.append("Adaptive\nSelection")
        elif "V3" in n.upper():
            short_names.append("Paper\nDecomp\nV3")
        elif "V2" in n.upper():
            short_names.append("Paper\nDecomp\nV2")
        elif "DECOMPOSITION" in n.upper():
            short_names.append("Paper\nDecomposition")
        elif "FEW_SHOT" in n.upper():
            short_names.append("Few-Shot\nClass")
        elif "ONE_SHOT" in n.upper():
            short_names.append("One-Shot\nClass")
        else:
            short_names.append(n)

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # ── 1. Accuracy Bar Chart ────────────────────────────────────────────────
    colors_acc = ["#4C72B0", "#55A868"]
    bars = axes[0].bar(short_names, accuracies, color="#4C72B0",
                       edgecolor="white", linewidth=0.8, width=0.45)
    axes[0].set_ylim(0, 1.15)
    axes[0].set_ylabel("Accuracy", fontsize=12)
    axes[0].set_title("Classification Accuracy (3-solver: LP / FOL / CSP)", fontsize=13, fontweight="bold")
    for bar, acc in zip(bars, accuracies):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                     f"{acc:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    # ── 2. Token Usage Stacked Bar Chart ─────────────────────────────────────
    x = np.arange(len(names))
    width = 0.45
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
        description="Compare PAPER_DECOMPOSITION_PROMPT vs ADAPTIVE_SELECTION_PROMPT "
                    "for 3-solver classification (LP / FOL / CSP)."
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

    # Map gold labels to 3-solver scheme (SAT -> CSP)
    for p in problems:
        p["gold_mapped"] = map_label(p.get("gold_solver", "UNKNOWN"), GOLD_LABEL_MAP)

    # Print dataset distribution
    gold_counts = pd.Series([p["gold_mapped"] for p in problems]).value_counts()
    print(f"\nGold label distribution (3-solver):\n{gold_counts.to_string()}\n")

    # Define prompt strategies to evaluate
    # Each tuple: (name, template, parser_type, label_map, temperature)
    strategies = [
        ("PAPER_DECOMPOSITION_PROMPT", PAPER_DECOMPOSITION_PROMPT, "decomposition", DECOMPOSITION_LABEL_MAP, 0),
        ("PAPER_DECOMPOSITION_PROMPT_V2", PAPER_DECOMPOSITION_PROMPT_V2, "decomposition", DECOMPOSITION_V2_LABEL_MAP, 0),
        ("PAPER_DECOMPOSITION_PROMPT_V3", PAPER_DECOMPOSITION_PROMPT_V3, "decomposition", DECOMPOSITION_V3_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT",  ADAPTIVE_SELECTION_PROMPT,  "adaptive",       ADAPTIVE_LABEL_MAP,      0),
        ("ADAPTIVE_SELECTION_PROMPT_V2", ADAPTIVE_SELECTION_PROMPT_V2, "adaptive_v2", ADAPTIVE_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_V2_1", ADAPTIVE_SELECTION_PROMPT_V2_1, "adaptive_v2", ADAPTIVE_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_V3", ADAPTIVE_SELECTION_PROMPT_V3, "adaptive_v3", ADAPTIVE_LABEL_MAP, 0),
        ("ADAPTIVE_SELECTION_PROMPT_V3_1", ADAPTIVE_SELECTION_PROMPT_V3_1, "adaptive_v3", ADAPTIVE_LABEL_MAP, 0),
        ("ONE_SHOT_CLASSIFICATION_PROMPT", ONE_SHOT_CLASSIFICATION_PROMPT, "one_shot", ONE_SHOT_LABEL_MAP, 0),
        ("FEW_SHOT_CLASSIFICATION_PROMPT", FEW_SHOT_CLASSIFICATION_PROMPT, "few_shot", FEW_SHOT_LABEL_MAP, 0),
    ]

    # Use a shared LLM client (resets usage per strategy)
    llm = LLMClient(model="openai/gpt-oss-120b")

    all_rows = []
    summary = {}

    for strat_idx, (name, template, parser_type, lmap, temp) in enumerate(strategies):
        # Cooldown between strategies to let the rate limit bucket refill
        if strat_idx > 0:
            print("\n  [Cooldown 5s between strategies...]")
            time.sleep(5)

        print(f"  [temp={temp}]")
        result = evaluate_prompt(llm, template, name, problems,
                                 parser=parser_type, label_map=lmap, temperature=temp)

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

    # Save combined CSV with detailed columns
    df_all = pd.DataFrame(all_rows)
    # Reorder columns for clarity
    col_order = [
        "prompt_strategy", "id", "problem_text", "full_prompt",
        "raw_response", "reasoning_trace",
        "raw_prediction", "prediction", "gold", "match",
        "prompt_tokens", "completion_tokens", "total_tokens",
    ]
    # Only include columns that exist
    col_order = [c for c in col_order if c in df_all.columns]
    df_all = df_all[col_order]
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
