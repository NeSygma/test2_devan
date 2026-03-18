import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.pipeline_router import LogicPipelineRouter
from solver_select_pipeline.dataset_loader import LogicDatasetLoader


def run_single_temperature(problems, temperature):
    """Run classification evaluation on a set of problems at a given temperature. Returns results list and total usage dict."""
    router = LogicPipelineRouter(temperature=temperature)
    router.reset_token_usage()
    
    results = []
    for problem in problems:
        usage_before = router.get_token_usage()
        
        text = problem.get('text', problem.get('premises', '') + '\n' + problem.get('conclusion', ''))
        
        predicted_solver = router.classify_solver_type(text)
        oneshot_solver = router.classify_solver_oneshot(text)
        gold_solver = problem.get('gold_solver', 'UNKNOWN')
        
        usage_after = router.get_token_usage()
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
    
    total_usage = router.get_token_usage()
    return results, total_usage


def generate_sweep_plots(summary_df, all_results_df):
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
                linewidth=2, markersize=8, label='Decomposition Pipeline')
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
        ax.set_title('Classification Accuracy vs Temperature', fontsize=14, fontweight='bold')
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
        ax.set_title('Total Token Usage vs Temperature', fontsize=14, fontweight='bold')
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

        results, total_usage = run_single_temperature(problems, temp)
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
    generate_sweep_plots(summary_df, all_df)


if __name__ == "__main__":
    main()
