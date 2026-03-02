import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from tqdm import tqdm
import pandas as pd
from solver_select_pipeline.pipeline_router import LogicPipelineRouter
from solver_select_pipeline.dataset_loader import LogicDatasetLoader

def main():
    parser = argparse.ArgumentParser(description="Evaluate logic problems with the Solver Choice Pipeline.")
    parser.add_argument("--dataset", type=str, default="folio", choices=["folio", "mixed", "custom_json", "custom_csv"], help="Dataset origin")
    parser.add_argument("--filepath", type=str, default=None, help="Path to custom dataset file")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of problems to evaluate (for testing)")
    parser.add_argument("--out", type=str, default="solver_pipeline_results.csv", help="Output CSV filename")
    parser.add_argument("--force-solver", type=str, default=None, choices=["PROVER9", "Z3", "PROLOG", "CONSTRAINT"], help="Force a specific solver for all problems")
    parser.add_argument("--eval-classification-only", action="store_true", help="Only evaluate the problem decomposition and solver classification.")
    
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
    print("Starting evaluation...")
    for problem in tqdm(problems):
        if args.eval_classification_only:
            # Classification Evaluation Mode (Pipeline vs One-shot)
            text = problem.get('text', problem.get('premises', '') + '\n' + problem.get('conclusion', ''))
            
            # 1. Decomposition Pipeline Prediction
            predicted_solver = router.classify_solver_type(text)
            # 2. One-shot Baseline Prediction
            oneshot_solver = router.classify_solver_oneshot(text)
            
            gold_solver = problem.get('gold_solver', 'UNKNOWN')
            
            results.append({
                "id": problem['id'],
                "gold_solver": gold_solver,
                "predicted_solver": predicted_solver,
                "oneshot_solver": oneshot_solver,
                "pipeline_match": predicted_solver == gold_solver,
                "oneshot_match": oneshot_solver == gold_solver,
                "text": text
            })
        else:
            # Full Execution Mode
            res = router.execute_problem(
                premises=problem.get('premises', ''), 
                conclusion=problem.get('conclusion', ''),
                forced_solver=args.force_solver
            )
            
            gold_label = str(problem.get('label', ''))
            match = False
            if gold_label.lower() == "true" and res['status'].lower() == "true":
                match = True
            elif gold_label.lower() in ["false", "uncertain"] and res['status'].lower() in ["false/uncertain", "uncertain", "false"]:
                match = True
                
            results.append({
                "id": problem['id'],
                "label": gold_label,
                "chosen_solver": res['solver'],
                "solver_status": res['status'],
                "match": match,
                "code": res['code'],
                "raw_output": res['output']
            })
        
    df = pd.DataFrame(results)
    df.to_csv(args.out, index=False)
    
    print(f"\nEvaluation complete. Results saved to {args.out}")
    if len(df) > 0:
        if args.eval_classification_only:
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
        else:
            acc = df['match'].mean()
            print(f"Overall Accuracy: {acc:.2%}")
            print("\nSolver Usage:")
            print(df['chosen_solver'].value_counts())
            print("\nSolver Outcomes:")
            print(df['solver_status'].value_counts())

if __name__ == "__main__":
    main()
