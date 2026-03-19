import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import time
import json
from string import Template
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.dataset_loader import LogicDatasetLoader
from solver_select_pipeline.prompts import (
    PAPER_DECOMPOSITION_PROMPT,
    PAPER_DECOMPOSITION_PROMPT_V2,
    ADAPTIVE_SELECTION_PROMPT,
)

# ── Label Mapping ──────────────────────────────────────────────────────────────
GOLD_LABEL_MAP = {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}

STRATEGIES = {
    "decomposition": {
        "name": "Paper Decomposition",
        "template": PAPER_DECOMPOSITION_PROMPT,
        "parser": "decomposition",
        "label_map": {"LP": "LP", "FOL": "FOL", "CSP": "CSP", "SAT": "CSP"}
    },
    "decomposition_v2": {
        "name": "Paper Decomposition V2",
        "template": PAPER_DECOMPOSITION_PROMPT_V2,
        "parser": "decomposition",
        "label_map": {"LP": "LP", "FOL": "FOL", "CSP/SAT/SMT": "CSP"}
    },
    "adaptive": {
        "name": "Adaptive Selection",
        "template": ADAPTIVE_SELECTION_PROMPT,
        "parser": "adaptive",
        "label_map": {"LP": "LP", "FOL": "FOL", "SAT": "CSP"}
    }
}

def map_label(label: str, label_map: dict = None) -> str:
    """Map a solver label using the given label map (3-solver scheme)."""
    if label_map is None:
        label_map = GOLD_LABEL_MAP
    return label_map.get(label.strip().upper(), "UNKNOWN")

def _parse_decomposition_response(response: str) -> str:
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
    except Exception:
        pass
    return "UNKNOWN"

def _parse_adaptive_response(response: str) -> str:
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    for solver in ["FOL", "LP", "SAT"]:
        if solver in clean:
            return solver
    return "UNKNOWN"

def _format_adaptive_prompt(problem_text: str) -> str:
    return Template(ADAPTIVE_SELECTION_PROMPT).safe_substitute(
        context=problem_text,
        question="(see context above)",
        options="(see context above)",
    )

def _parse_oneshot_response(response: str) -> str:
    if not response:
        return "UNKNOWN"
    clean = response.strip().upper()
    for s in ["LP", "FOL", "CSP", "SAT"]:
        if s in clean:
            return s
    return "UNKNOWN"

ONESHOT_SYS_PROMPT = (
    "You are an expert logician. Your task is to classify the provided logical reasoning problem into one of four solver types:\n"
    "- LP (Logic Programming)\n"
    "- FOL (First-order Logic)\n"
    "- CSP (Constraint Satisfaction Problem)\n"
    "- SAT (Boolean Satisfiability)\n\n"
    "Respond ONLY with the exact name of the category (LP, FOL, CSP, or SAT).\n\n"
    "Example 1:\n"
    "Problem Statement:\n"
    "Three people sit in a row. Alice does not sit next to Bob. Charlie sits on the left. Who sits in the middle?\n"
    "Category: CSP\n"
)


def run_single_temperature(problems, temperature, prompt_key):
    """Run classification evaluation on a set of problems at a given temperature."""
    strategy = STRATEGIES[prompt_key]
    parser_type = strategy["parser"]
    prompt_template = strategy["template"]
    label_map = strategy["label_map"]

    llm = LLMClient(model="openai/gpt-oss-120b")
    llm.reset_usage()
    
    results = []
    for problem in tqdm(problems, desc=f"Temp={temperature}"):
        usage_before = llm.get_total_usage()
        
        text = problem.get('text', problem.get('premises', '') + '\n' + problem.get('conclusion', ''))
        gold_solver = map_label(problem.get('gold_solver', 'UNKNOWN'), GOLD_LABEL_MAP)
        
        # 1. Pipeline prompt
        if parser_type == "adaptive":
            prompt = _format_adaptive_prompt(text)
        else:
            prompt = prompt_template.format(problem=text)
            
        try:
            response, _, _ = llm.generate(
                prompt=prompt,
                system_prompt="", 
                temperature=temperature,
                max_completion_tokens=4096,
                max_retries=5
            )
            raw_pred = _parse_adaptive_response(response) if parser_type == "adaptive" else _parse_decomposition_response(response)
        except Exception:
            raw_pred = "UNKNOWN"
        predicted_solver = map_label(raw_pred, label_map)

        # 2. One-shot baseline
        oneshot_user = f"Problem Statement:\n{text}\nCategory:\n"
        try:
            oneshot_resp, _, _ = llm.generate(
                prompt=oneshot_user,
                system_prompt=ONESHOT_SYS_PROMPT,
                temperature=temperature,
                max_retries=5
            )
            raw_oneshot = _parse_oneshot_response(oneshot_resp)
        except Exception:
            raw_oneshot = "UNKNOWN"
            
        oneshot_solver = map_label(raw_oneshot, STRATEGIES["decomposition"]["label_map"])

        usage_after = llm.get_total_usage()
        problem_tokens = {
            "prompt_tokens": usage_after["prompt_tokens"] - usage_before["prompt_tokens"],
            "completion_tokens": usage_after["completion_tokens"] - usage_before["completion_tokens"],
            "total_tokens": usage_after["total_tokens"] - usage_before["total_tokens"],
        }
        
        results.append({
            "id": problem['id'],
            "temperature": temperature,
            "gold_solver": gold_solver,
            "predicted_solver": predicted_solver,
            "oneshot_solver": oneshot_solver,
            "pipeline_match": predicted_solver == gold_solver,
            "oneshot_match": oneshot_solver == gold_solver,
            "prompt_tokens": problem_tokens["prompt_tokens"],
            "completion_tokens": problem_tokens["completion_tokens"],
            "total_tokens": problem_tokens["total_tokens"],
        })
    
    total_usage = llm.get_total_usage()
    return results, total_usage


def generate_sweep_plots(summary_df, all_results_df, pipeline_name="Decomposition Pipeline"):
    """Generate accuracy vs temperature and token usage vs temperature plots."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker

        os.makedirs('media', exist_ok=True)

        # --- Plot 1: Accuracy vs Temperature ---
        fig, ax = plt.subplots(figsize=(10, 6))
        temps = summary_df['temperature'].tolist()
        temp_labels = [str(t) for t in temps]

        ax.plot(temp_labels, summary_df['pipeline_accuracy'], 'o-', color='#4C72B0',
                linewidth=2, markersize=8, label=pipeline_name)
        ax.plot(temp_labels, summary_df['oneshot_accuracy'], 's--', color='#DD8452',
                linewidth=2, markersize=8, label='One-shot Baseline')
        # Annotate each point with temperature + accuracy value
        for i, t in enumerate(temps):
            ax.annotate(f"T={t}\n{summary_df['pipeline_accuracy'].iloc[i]:.1%}",
                        (temp_labels[i], summary_df['pipeline_accuracy'].iloc[i]),
                        textcoords="offset points", xytext=(0, 12), ha='center', fontsize=8,
                        color='#4C72B0', fontweight='bold')
            ax.annotate(f"{summary_df['oneshot_accuracy'].iloc[i]:.1%}",
                        (temp_labels[i], summary_df['oneshot_accuracy'].iloc[i]),
                        textcoords="offset points", xytext=(0, -16), ha='center', fontsize=8,
                        color='#DD8452', fontweight='bold')

        ax.set_xlabel('Temperature', fontsize=12)
        ax.set_ylabel('Accuracy', fontsize=12)
        ax.set_title(f'Classification Accuracy vs Temperature ({pipeline_name})', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plot_file = os.path.join('media', 'temp_sweep_accuracy.png')
        plt.savefig(plot_file, dpi=150)
        plt.close()
        print(f"Accuracy plot saved to {plot_file}")

        # --- Plot 2: Token Usage vs Temperature ---
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.35
        x_pos = range(len(temps))

        bars_prompt = ax.bar([p - bar_width/2 for p in x_pos], summary_df['total_prompt_tokens'],
                             bar_width, label='Prompt Tokens', color='#4C72B0', edgecolor='white')
        bars_completion = ax.bar([p + bar_width/2 for p in x_pos], summary_df['total_completion_tokens'],
                                 bar_width, label='Completion Tokens', color='#DD8452', edgecolor='white')

        # Annotate bars with temperature and token counts
        for i, t in enumerate(temps):
            total = summary_df['total_tokens'].iloc[i]
            ax.text(i, max(summary_df['total_prompt_tokens'].iloc[i],
                           summary_df['total_completion_tokens'].iloc[i]) + total * 0.02,
                    f"T={t}\n{total:,} total", ha='center', fontsize=8, fontweight='bold')

        ax.set_xlabel('Temperature', fontsize=12)
        ax.set_ylabel('Token Count', fontsize=12)
        ax.set_title(f'Total Token Usage vs Temperature ({pipeline_name})', fontsize=14, fontweight='bold')
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(temp_labels)
        ax.legend(loc='upper left')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{int(val):,}'))
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plot_file = os.path.join('media', 'temp_sweep_tokens.png')
        plt.savefig(plot_file, dpi=150)
        plt.close()
        print(f"Token usage plot saved to {plot_file}")

    except ImportError:
        print("\nmatplotlib is not installed. Skipping visualization.")


def main():
    parser = argparse.ArgumentParser(description="Evaluate solver classification across multiple temperature values.")
    parser.add_argument("--prompt", type=str, default="decomposition", choices=list(STRATEGIES.keys()),
                        help="Prompt strategy to evaluate")
    parser.add_argument("--dataset", type=str, default="mixed",
                        choices=["folio", "mixed", "custom_json", "custom_csv"], help="Dataset origin")
    parser.add_argument("--filepath", type=str, default=None, help="Path to custom dataset file")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of problems per dataset")
    parser.add_argument("--temperatures", type=str, default="0.0,0.01,0.1,0.3,0.5,0.7,1.0",
                        help="Comma-separated temperature values to sweep")
    parser.add_argument("--out", type=str, default="temp_sweep_results.csv", help="Output CSV filename")

    args = parser.parse_args()

    temperatures = [float(t.strip()) for t in args.temperatures.split(",")]
    print(f"Temperature sweep: {temperatures}")
    print(f"Prompt Strategy: {STRATEGIES[args.prompt]['name']}")
    print(f"Using 3-solver mapping (LP, FOL, CSP/SAT->CSP)")

    # Load dataset once
    print(f"Loading dataset: {args.dataset}")
    if args.dataset == "folio":
        problems = LogicDatasetLoader.load_folio_huggingface(limit=args.limit)
    elif args.dataset == "mixed":
        problems = LogicDatasetLoader.load_mixed_datasets(limit_per_dataset=args.limit)
    elif args.dataset == "custom_json":
        problems = LogicDatasetLoader.load_custom_json(args.filepath)[:args.limit]
    elif args.dataset == "custom_csv":
        problems = LogicDatasetLoader.load_custom_csv(args.filepath)[:args.limit]
    print(f"Loaded {len(problems)} problems.\n")

    all_results = []
    summary_rows = []

    for temp in temperatures:
        print(f"\n{'='*60}")
        print(f"  Running evaluation at temperature = {temp}")
        print(f"{'='*60}")

        results, total_usage = run_single_temperature(problems, temp, args.prompt)
        all_results.extend(results)

        df_temp = pd.DataFrame(results)

        pipe_acc = df_temp['pipeline_match'].mean() if len(df_temp) > 0 else 0
        one_acc = df_temp['oneshot_match'].mean() if len(df_temp) > 0 else 0

        row = {
            "temperature": temp,
            "num_problems": len(df_temp),
            "pipeline_accuracy": pipe_acc,
            "oneshot_accuracy": one_acc,
            "total_prompt_tokens": total_usage["prompt_tokens"],
            "total_completion_tokens": total_usage["completion_tokens"],
            "total_tokens": total_usage["total_tokens"],
        }

        print(f"  Pipeline Accuracy: {pipe_acc:.2%}")
        print(f"  One-shot Accuracy: {one_acc:.2%}")
        print(f"  Total Tokens: {total_usage['total_tokens']:,}")
        summary_rows.append(row)

    # Save all per-problem results
    all_df = pd.DataFrame(all_results)
    all_df.to_csv(args.out, index=False)
    print(f"\nAll results saved to {args.out}")

    # Print summary table
    summary_df = pd.DataFrame(summary_rows)
    print(f"\n{'='*60}")
    print("  TEMPERATURE SWEEP SUMMARY")
    print(f"{'='*60}")
    print(summary_df.to_string(index=False))
    print(f"{'='*60}")

    # Generate plots
    generate_sweep_plots(summary_df, all_df, pipeline_name=STRATEGIES[args.prompt]['name'])


if __name__ == "__main__":
    main()
