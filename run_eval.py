import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.pipeline_router import LogicPipelineRouter
from solver_select_pipeline.dataset_loader import LogicDatasetLoader

def main():
    parser = argparse.ArgumentParser(description="Evaluate solver classification with the Logic Pipeline.")
    parser.add_argument("--dataset", type=str, default="folio", choices=["folio", "mixed", "custom_json", "custom_csv"], help="Dataset origin")
    parser.add_argument("--filepath", type=str, default=None, help="Path to custom dataset file")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of problems to evaluate (for testing)")
    parser.add_argument("--out", type=str, default="solver_pipeline_results.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset: {args.dataset}")
    if args.dataset == "folio":
        problems = LogicDatasetLoader.load_folio_huggingface(limit=args.limit)
    elif args.dataset == "mixed":
        problems = LogicDatasetLoader.load_mixed_datasets(limit_per_dataset=args.limit)
    elif args.dataset == "custom_json":
        problems = LogicDatasetLoader.load_custom_json(args.filepath)[:args.limit]
    elif args.dataset == "custom_csv":
        problems = LogicDatasetLoader.load_custom_csv(args.filepath)[:args.limit]
        
    print(f"Loaded {len(problems)} problems.")
    
    # Initialize Pipeline
    router = LogicPipelineRouter()
    
    results = []
    router.reset_token_usage()  # Reset counters before evaluation
    print("Starting evaluation...")
    for problem in tqdm(problems):
        # Snapshot token usage before this problem
        usage_before = router.get_token_usage()
        
        text = problem.get('text', problem.get('premises', '') + '\n' + problem.get('conclusion', ''))
        
        # 1. Decomposition Pipeline Prediction
        predicted_solver = router.classify_solver_type(text)
        # 2. One-shot Baseline Prediction
        oneshot_solver = router.classify_solver_oneshot(text)
        
        gold_solver = problem.get('gold_solver', 'UNKNOWN')
        
        # Compute per-problem token delta
        usage_after = router.get_token_usage()
        problem_tokens = {
            "prompt_tokens": usage_after["prompt_tokens"] - usage_before["prompt_tokens"],
            "completion_tokens": usage_after["completion_tokens"] - usage_before["completion_tokens"],
            "total_tokens": usage_after["total_tokens"] - usage_before["total_tokens"],
        }
        
        results.append({
            "id": problem['id'],
            "gold_solver": gold_solver,
            "predicted_solver": predicted_solver,
            "oneshot_solver": oneshot_solver,
            "pipeline_match": predicted_solver == gold_solver,
            "oneshot_match": oneshot_solver == gold_solver,
            "text": text,
            "prompt_tokens": problem_tokens["prompt_tokens"],
            "completion_tokens": problem_tokens["completion_tokens"],
            "total_tokens": problem_tokens["total_tokens"],
        })
        
    df = pd.DataFrame(results)
    df.to_csv(args.out, index=False)
    
    # Print total token usage summary
    total_usage = router.get_token_usage()
    print(f"\n{'='*50}")
    print(f"TOKEN USAGE SUMMARY")
    print(f"{'='*50}")
    print(f"Total Prompt Tokens:     {total_usage['prompt_tokens']:,}")
    print(f"Total Completion Tokens: {total_usage['completion_tokens']:,}")
    print(f"Total Tokens:            {total_usage['total_tokens']:,}")
    print(f"{'='*50}")
    
    print(f"\nEvaluation complete. Results saved to {args.out}")
    if len(df) > 0:
        pipe_acc = df['pipeline_match'].mean()
        one_acc = df['oneshot_match'].mean()
        print(f"Pipeline (Decomposition) Classification Accuracy: {pipe_acc:.2%}")
        print(f"One-shot Baseline Classification Accuracy: {one_acc:.2%}")
        
        print("\n--- Pipeline (Decomposition) Matrix ---")
        print(pd.crosstab(df['gold_solver'], df['predicted_solver']))
        
        print("\n--- One-shot Baseline Matrix ---")
        print(pd.crosstab(df['gold_solver'], df['oneshot_solver']))
        
        # Generate Visualization
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            
            # 1. Accuracy Bar Chart
            acc_df = pd.DataFrame({'Method': ['Decomposition Pipeline', 'One-shot Baseline'], 'Accuracy': [pipe_acc, one_acc]})
            sns.barplot(x='Method', y='Accuracy', data=acc_df, ax=axes[0], palette='viridis')
            axes[0].set_ylim(0, 1)
            axes[0].set_title('Classification Accuracy Comparison')
            for i, v in enumerate([pipe_acc, one_acc]):
                axes[0].text(i, v + 0.02, f"{v:.2%}", ha='center')
                
            # 2. Confusion Matrices
            labels = ["LP", "FOL", "CSP", "SAT"]
            
            pipe_cm = pd.crosstab(df['gold_solver'], df['predicted_solver']).reindex(index=labels, columns=labels, fill_value=0)
            sns.heatmap(pipe_cm, annot=True, fmt='d', cmap='Blues', ax=axes[1])
            axes[1].set_title('Decomposition Pipeline Matrix')
            axes[1].set_xlabel('Predicted Solver')
            axes[1].set_ylabel('Gold Solver')
            
            oneshot_cm = pd.crosstab(df['gold_solver'], df['oneshot_solver']).reindex(index=labels, columns=labels, fill_value=0)
            sns.heatmap(oneshot_cm, annot=True, fmt='d', cmap='Blues', ax=axes[2])
            axes[2].set_title('One-shot Baseline Matrix')
            axes[2].set_xlabel('Predicted Solver')
            axes[2].set_ylabel('Gold Solver')
            
            plt.tight_layout()
            os.makedirs('media', exist_ok=True)
            plot_file = os.path.join('media', 'classification_results_plot.png')
            plt.savefig(plot_file)
            print(f"\nVisualization saved to {plot_file}")
        except ImportError:
            print("\nmatplotlib and/or seaborn are not installed. Skipping visualization.")
        
        # Generate Token Usage Plot
        _generate_token_usage_plot(df, total_usage)

def _generate_token_usage_plot(df, total_usage):
    """Generates a stacked bar chart of per-problem token usage and saves it to media/."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        
        fig, ax = plt.subplots(figsize=(max(10, len(df) * 0.8), 6))
        
        x = range(len(df))
        problem_labels = [str(pid) for pid in df['id']]
        prompt_tokens = df['prompt_tokens'].tolist()
        completion_tokens = df['completion_tokens'].tolist()
        
        # Stacked bar chart
        bars_prompt = ax.bar(x, prompt_tokens, label='Prompt Tokens', color='#4C72B0', edgecolor='white', linewidth=0.5)
        bars_completion = ax.bar(x, completion_tokens, bottom=prompt_tokens, label='Completion Tokens', color='#DD8452', edgecolor='white', linewidth=0.5)
        
        ax.set_xlabel('Problem ID', fontsize=12)
        ax.set_ylabel('Token Count', fontsize=12)
        ax.set_title('Token Usage Per Problem', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(problem_labels, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper right')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{int(val):,}'))
        
        # Annotate total usage
        total_text = (
            f"Total Tokens: {total_usage['total_tokens']:,}\n"
            f"  Prompt: {total_usage['prompt_tokens']:,}\n"
            f"  Completion: {total_usage['completion_tokens']:,}"
        )
        ax.text(0.98, 0.95, total_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='gray', alpha=0.9))
        
        plt.tight_layout()
        os.makedirs('media', exist_ok=True)
        plot_file = os.path.join('media', 'token_usage_plot.png')
        plt.savefig(plot_file, dpi=150)
        plt.close()
        print(f"Token usage plot saved to {plot_file}")
    except ImportError:
        print("\nmatplotlib is not installed. Skipping token usage visualization.")

if __name__ == "__main__":
    main()
