import json
import pandas as pd
from datasets import load_dataset, VerificationMode
from typing import List, Dict, Any

class LogicDatasetLoader:
    """
    A generic loader to pull out premises, conclusions, and labels from various dataset formats.
    """
    @staticmethod
    def load_folio_huggingface(split: str = "validation", limit: int = None) -> List[Dict[str, Any]]:
        """
        Loads the Yale FOLIO dataset from HuggingFace.
        Returns a list of dicts: [{"id": ..., "premises": str, "conclusion": str, "label": str}]
        """
        try:
            dataset = load_dataset("yale-nlp/FOLIO", verification_mode=VerificationMode.NO_CHECKS)
            df = pd.DataFrame(dataset[split])
            
            records = []
            for idx, row in df.iterrows():
                if limit and idx >= limit:
                    break
                    
                # Format premises exactly as in the original notebooks
                premise_text = "\\n".join(row['premises']) if isinstance(row['premises'], list) else str(row['premises'])
                
                records.append({
                    "id": row.get('example_id', str(idx)),
                    "premises": premise_text,
                    "conclusion": str(row['conclusion']),
                    "label": str(row['label'])
                })
            return records
        except Exception as e:
            print(f"Error loading FOLIO: {e}")
            return []

    @staticmethod
    def load_custom_json(filepath: str) -> List[Dict[str, Any]]:
        """
        Loads a custom JSON array format.
        Assuming format: [{"id": "1", "premises": "...", "conclusion": "...", "label": "True"}]
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading JSON {filepath}: {e}")
            return []
            
    @staticmethod
    def load_custom_csv(filepath: str) -> List[Dict[str, Any]]:
        """
        Loads a custom CSV format.
        Assuming columns: id, premises, conclusion, label
        """
        try:
            df = pd.read_csv(filepath)
            records = []
            for _, row in df.iterrows():
                records.append({
                    "id": str(row.get('id', '')),
                    "premises": str(row.get('premises', '')),
                    "conclusion": str(row.get('conclusion', '')),
                    "label": str(row.get('label', ''))
                })
            return records
        except Exception as e:
            print(f"Error loading CSV {filepath}: {e}")
            return []
