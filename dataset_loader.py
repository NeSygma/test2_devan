import json
import random
import pandas as pd
from datasets import load_dataset, VerificationMode
from typing import List, Dict, Any

class LogicDatasetLoader:
    """
    A generic loader to pull out premises, conclusions, and labels from various dataset formats
    and assign gold standard solver types as specified by arXiv:2510.06774v1.
    """
    
    @staticmethod
    def load_proofwriter(limit: int = 5) -> List[Dict[str, Any]]:
        """LP: ProofWriter dataset."""
        records = []
        try:
            # We try a common ProofWriter source. If it fails due to network/auth, we provide a fallback
            dataset = load_dataset("tasksource/proofwriter", split="validation", verification_mode=VerificationMode.NO_CHECKS)
            for idx, row in enumerate(dataset):
                if limit and idx >= limit: break
                records.append({
                    "id": f"proofwriter_{idx}",
                    "text": str(row.get('context', '')) + " \n " + str(row.get('question', '')),
                    "gold_solver": "LP"
                })
        except Exception as e:
            print(f"Error loading ProofWriter: {e}")
            # Fallback mock for testing the classification pipeline
            records.append({
                "id": "proofwriter_mock_1",
                "text": "All cats are mammals. Fluffy is a cat. Is Fluffy a mammal?",
                "gold_solver": "LP"
            })
        return records

    @staticmethod
    def load_folio_huggingface(limit: int = 5) -> List[Dict[str, Any]]:
        """FOL: Yale FOLIO dataset."""
        records = []
        try:
            dataset = load_dataset("yale-nlp/FOLIO", split="validation", verification_mode=VerificationMode.NO_CHECKS)
            df = pd.DataFrame(dataset)
            for idx, row in df.iterrows():
                if limit and idx >= limit: break
                premise_text = "\n".join(row['premises']) if isinstance(row['premises'], list) else str(row['premises'])
                records.append({
                    "id": f"folio_{idx}",
                    "text": premise_text + "\nConclusion: " + str(row['conclusion']),
                    "gold_solver": "FOL"
                })
        except Exception as e:
            print(f"Error loading FOLIO: {e}")
            records.append({
                "id": "folio_mock_1",
                "text": "All employees who work in sales must attend the conference. No temps are employees. Conclusion: No temps attend the conference.",
                "gold_solver": "FOL"
            })
        return records
        
    @staticmethod
    def load_logical_deduction(limit: int = 5) -> List[Dict[str, Any]]:
        """CSP: LogicalDeduction (BBH)."""
        records = []
        try:
            dataset = load_dataset("lukaemon/bbh", "logical_deduction_five_objects", split="test", verification_mode=VerificationMode.NO_CHECKS)
            for idx, row in enumerate(dataset):
                if limit and idx >= limit: break
                records.append({
                    "id": f"logdeduc_{idx}",
                    "text": str(row.get('input', '')),
                    "gold_solver": "CSP"
                })
        except Exception as e:
            print(f"Error loading LogicalDeduction: {e}")
            records.append({
                "id": "logdeduc_mock_1",
                "text": "A is next to B. C is on the far left. Where is D?",
                "gold_solver": "CSP"
            })
        return records

    @staticmethod
    def load_ar_lsat(limit: int = 5) -> List[Dict[str, Any]]:
        """SAT: AR-LSAT (Analytical Reasoning)."""
        records = []
        try:
            dataset = load_dataset("tasksource/lsat-ar", split="train", verification_mode=VerificationMode.NO_CHECKS)
            for idx, row in enumerate(dataset):
                if limit and idx >= limit: break
                records.append({
                    "id": f"arlsat_{idx}",
                    "text": str(row.get('context', '')) + "\n" + str(row.get('question', '')) + "\n" + str(row.get('options', '')),
                    "gold_solver": "SAT"
                })
        except Exception as e:
            print(f"Error loading AR-LSAT: {e}")
            records.append({
                "id": "arlsat_mock_1",
                "text": "Seven passengers are boarding a train. A must board before B. C boards third. Question: Who boards first?",
                "gold_solver": "SAT"
            })
        return records

    @staticmethod
    def load_mixed_datasets(limit_per_dataset: int = 5) -> List[Dict[str, Any]]:
        """
        Loads and interleaves ProofWriter, FOLIO, LogicalDeduction, and AR-LSAT 
        for evaluation of solver classification.
        """
        all_records = []
        all_records.extend(LogicDatasetLoader.load_proofwriter(limit_per_dataset))
        all_records.extend(LogicDatasetLoader.load_folio_huggingface(limit_per_dataset))
        all_records.extend(LogicDatasetLoader.load_logical_deduction(limit_per_dataset))
        all_records.extend(LogicDatasetLoader.load_ar_lsat(limit_per_dataset))
        
        # Shuffle to test the pipeline's robustness
        random.shuffle(all_records)
        return all_records

    @staticmethod
    def load_custom_json(filepath: str) -> List[Dict[str, Any]]:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON {filepath}: {e}")
            return []
            
    @staticmethod
    def load_custom_csv(filepath: str) -> List[Dict[str, Any]]:
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
