import argparse
from tqdm import tqdm
import pandas as pd
from solver_pipeline.pipeline_router import LogicPipelineRouter
from solver_pipeline.dataset_loader import LogicDatasetLoader

def main():
    parser = argparse.ArgumentParser(description="Evaluate logic problems with the Solver Choice Pipeline.")
    parser.add_argument("--dataset", type=str, default="folio", choices=["folio", "custom_json", "custom_csv"], help="Dataset origin")
    parser.add_argument("--filepath", type=str, default=None, help="Path to custom dataset file")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of problems to evaluate (for testing)")
    parser.add_argument("--out", type=str, default="solver_pipeline_results.csv", help="Output CSV filename")
    parser.add_argument("--force-solver", type=str, default=None, choices=["PROVER9", "Z3", "PROLOG", "CONSTRAINT"], help="Force a specific solver for all problems")
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset: {args.dataset}")
    if args.dataset == "folio":
        problems = LogicDatasetLoader.load_folio_huggingface(limit=args.limit)
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
        res = router.execute_problem(
            premises=problem['premises'], 
            conclusion=problem['conclusion'],
            forced_solver=args.force_solver
        )
        
        # Determine match correctly based on dataset exact string (assuming 'True', 'False', 'Uncertain')
        gold_label = problem['label']
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
    
    print(f"\\nEvaluation complete. Results saved to {args.out}")
    if len(df) > 0:
        acc = df['match'].mean()
        print(f"Overall Accuracy: {acc:.2%}")
        print("\\nSolver Usage:")
        print(df['chosen_solver'].value_counts())
        print("\\nSolver Outcomes:")
        print(df['solver_status'].value_counts())

if __name__ == "__main__":
    main()
